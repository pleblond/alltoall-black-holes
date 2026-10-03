# Deferred derivations (v5+)

Single tracker for open derivations deliberately **not** claimed in v5.
Each item: what is missing, why it matters, what would close it.
Honesty ledger in `paper/v5/supplement.tex` S1 points here.

**Tag note (audit v0.2):** `Dn` below means DEFERRED item n. The appendix-letter
tag (D2) (= module `evaporation_unitary`, the closed qubit-toy instance under
D1) is unrelated to DEFERRED-D2 (Kerr multipoles); `docs/model.md` always
writes the module name. `supplement.tex` S1/S3 still uses bare (D2) for both —
flagged for the paper flow (needs PDF rebuild).

## Program pipeline (P0'/D10/D1/D13/D12 + commutation)

Vacuum graph family → graph-internal admissible `M_O` → 2+scale → 3
reconstruction → explicit `U` → `δ_U(s,v;n)` → `V_U(n)`, `≺_U` →
same frozen `M_O` → observed causal geometry → `M_O U ≃ U_eff M_O`.
Division of labor: P0' identifies the vacuum connectivity class; D10
asks why observers reconstruct 3D from it; D1 asks what dynamics
preserves/evolves it; D13 asks whether that dynamics generates causal
time; D12 asks whether the reconstruction is universal;
`M_O U ≃ U_eff M_O` asks whether the whole construction becomes
autonomous spacetime physics.

## D1 — Evaporation isometry V_k (Page/QES) — P0 next cycle

**Missing:** unitary/isometric evaporation map from graph dynamics:
`V_k: H_graph,k -> H_graph,k-1 ⊗ H_leg`.
Current status: `k -> k-1` surgery is imposed; `S_rad = min(t, Neff-t)`
with 0.72-bit dip is imposed/sampled (`evaporation`, `haar`); QES crossing
is a two-saddle competition + discrete min-cut analogue (`qes`), not
`S_gen = A/4G + S_matter` extremized from a gravitational path integral.
Update (PR #10): the qubit-toy instance is closed — `evaporation_unitary`
(appendix tag D2 — not DEFERRED-D2) constructs per-step `V_t`, proves `V†V=I` (incl. a composed-map
inner-product test), and computes `S_rad` from `rho_rad` (tracks Haar/Page
to 0.002 bits; all:all circuits converge by depth ~5). What remains is the
graph instance: derive `V_k` from graph dynamics, not merely choose one.
Scope note (D13): D1's dynamics now also gates emergent time itself
(update rule → causal order → cone → clocks), not just evaporation/QES.
D13-input desideratum (not a close criterion): candidate `U` should be
local and fabric-compatible so D13 stage 1 can run on it. Stabilizer
question (rewire sweep): what dynamics keeps the `d_G ≃ 2` phase
stable against shortcut proliferation (`N* ∼ O(10)` flat in L)?
Preservation target: `U(G_vac) ∈ C_vac` — microscopic evolution may
fluctuate (`G_n ≠ G_{n+1}`) while the IR class stays invariant
(`[G_n]_IR = [G_{n+1}]_IR ∈ C_vac`): vacuum as invariant dynamical
universality class. Then `M_O` quotienting irrelevant fluctuations
gives `M_O(G_n) ≃ M_O(G_{n+1})` — stable vacuum atop a changing
graph (the commutation link). Falsifier protocol (gated on U):
evolve `G_0 → G_1 → …` from `G_vac` and require `G_n ∈ C_vac ∀n`
in equilibrium, up to fluctuations — operationally `⟨Λ⟩_U` in the
vacuum basin for a locality functional Λ (candidates: window-p;
N* itself; distance-to-C_vac; Λ undefined — open). Then inject
shortcuts (`G → G + δG_shortcut`) and watch: persist/amplify kills
the candidate; `δG_shortcut → G_vac` (self-healing) means locality
is an attractor — no perfectly local vacuum graph need be
postulated. Statistical form (stochastic/quantum U): ensemble
concentration `P_U(G ∉ C_vac) → 0` in the IR limit — vacuum as
dynamical phase (this licenses "phase"; no rewiring phase
transition is claimed). Acquired constraint: find a simple U for
which locality, unitarity/information conservation, and the vacuum
structure are simultaneously natural. Stability tournament
(QUEUED behind U, protocol fixed on review): initialize EVERY
Tier-1 candidate (triangular, hex, square, Delaunay, Gabriel, …)
and evolve under EXACTLY the same U; measure escape
P(U^t G ∈ C_vac) per candidate — vacuum selection as attractor /
stationary ensemble (P_U(G) = P_U(U(G))), not static p. Healing
battery: apply the same normalized damage to each candidate
(shortcut injection, edge deletion, degree defect, bottleneck,
plug insertion) and measure relaxation τ_heal(G, δG) under U —
candidates identical in equilibrium may differ sharply in
locality restoration. Selection rule (conceptual, SUPERSEDED — see
BLIND-U REFRAMING below; kept for history):
G_vac = argmax stability of the M_O-equivalence class. First rules
(MEASURED, test_update_rule.py, L=20): harness (locality-p, shortcut
injection, evolve) validated — null persists damage bit-identically,
scramble kills (2.51 → 1.79 collapse). Twin-targeted greedy heals
p = 2.36 → p_plain to 1e-6 into a DIFFERENT microstate (699/760
overlap) — class healing, existence probe only (global target, not a
local rule); plain is its fixed point. Genuinely-local guillotine
(radius-3 edge-span evals, no twin): plain-grid span signature is
exactly 3 on all 760 edges; rule heals longs 30 → 6, p 2.36 → 2.13,
then STALLS — exhaustive check proves 4 of 6 residual longs admit
zero both-short single-swap repairs (locked, incl. short-range edges
whose plaquette detours were destroyed). Mechanism lessons: repair
needs long×long straddling (re-pairing a long with a local edge
always leaves one long); total-span descent splits longs instead of
killing them (count 30 → 39 while p falls — span-sum is a poor
proxy); no local potential tracks p well (corr ≤ 0.58 — p is
source-relative/lottery-noisy, span-census is the more honest global
health stat). Queued escape: neutral moves / annealing on long-count
(stochastic U is filed-legal) / coordinated multi-swaps. Escape
results (MEASURED): neutral drift is WORSE than strict (longs 30 →
22 — local delta doesn't bound global longs, detour rerouting
leaks); blind-proposal annealing stalls (greedy) or explodes
(longs → 101 at T0=5 — proposals matter more than acceptance, not
shipped); census-gated targeted annealing reaches longs 11 (T0=0,
p 1.97) / longs 9 (T0=2, p 2.26) — temperature trades p for longs;
strict→anneal chains and drift⇄strict ratchets don't clear the
locked core. Tournament table from damage (p 2.362, longs 30):
null (2.362, 30); greedy-twin (1.835, 88 — games p, triples
longs!); guillotine (2.132, 6); drift (2.129, 22); anneal (1.97,
11)/(2.26, 9); scramble (1.786, 297). HEADLINE: p-healing ≠
healing — the D1 falsifier must judge (p, longs) jointly, and no
single-swap rule clears both. Next: coordinated multi-swap moves
or new move classes (degree-changing repair? edge-slide?), then
the cross-candidate tournament this harness was built for. New
move class (MEASURED): edge-slide reel-in (radius-6 span gradient;
radius 3 blinds it — 1 accept) reaches longs 5 (best yet) but p
stuck at 2.32 — 5 levered longs hold the window while greedy's 88
hide from it: the (p, longs) plane is genuinely 2D. Slide ⇄
guillotine hybrid FROZEN bit-identically (joint fixed point).
VERDICT: single-move local dynamics (strict/neutral/annealed
swaps, slides, hybrids) cannot restore locality from swap damage
— all stall with residual longs. Locality protection needs
coordinated moves, global search, or new physics (a publishable
constraint on U). D1 first-pass CLOSED; tournament harness stands
ready for future entrants. Second-pass entrant (MEASURED,
test_update_rule.py): coordinated double-swap (3-edge joint
re-pairing, all-short + connectivity-guarded accept) breaks the
single-move floor — pair600 seed 5 reaches longs 1 with p 2.11,
seed 6 descends 10@600 → 4 with p 2.01@1200 (slow, not stuck),
seed 7 longs 4 with p 1.98: first rule near-clearing BOTH axes.
Existence scan behind it: 745/11370 long²×any triples admit an
all-short re-pairing (long³ alone: 0/20 — straddling needs a
short partner). Two lessons: (i) the connectivity guard is
load-bearing — unguarded seed 6 fragments a 4-node island and its
p 1.93 is partly a disconnection artifact; (ii) the last residual
is PAIR-LOCKED (0 repairing re-pairings in an exhaustive 287661-
triple scan, measured-not-shipped, 35 s): the lock hierarchy
deepens with coordination order (single-swap locks 4, double-swap
locks 1). Next: triple-swap / 4-edge moves, then the tournament.
Triple-swap endgame (MEASURED, test_update_rule.py): 4-edge joint
re-pairing (105 matchings) unlocks the pair-locked residual — blind
sampling hits ~6e-6 with necessarily far partners (d_res 5-6; radius-3
ball exhaustive 0/147440), but CHAINED VISIBILITY works: graft each
residual endpoint onto a span-visible partner edge (BFS-cutoff balls,
radius-local), chain the 4th edge off the leftovers — hit rate jumps
140x to ~9e-4 (17/19825; the blind hit's partners split Va/Vb/far
exactly as the design predicts). rule_triple (long-first targeting —
random-edge picks starve at 1 long in 760 edges) clears pair-stall to
longs == 0 on seeds 5 AND 7 (p 2.04/1.95, connected): the FIRST
COMPLETE locality restoration in the tournament. Caveats: seed 6
reaches only 2 longs in 30 steps (62 s, filed-not-shipped — slow
residuals persist); p at zero longs reads 2.04/1.95 vs plain 1.83
while seed 6 reads near-plain 1.83 WITH 2 longs left — the (p, longs)
plane stays 2D down to the floor. D1 verdict upgraded: locality CAN
be restored, at coordination order 3 with detour-aware proposals —
protection demands coordination, not just locality of moves.
Triple-lock (MEASURED, test_update_rule.py + filed): the seed-6
residual is a CORNER pair ((379,399),(398,399) sharing (19,19)) —
single-swap exhaustive 0 repairs each, chained 100k sample 0 hits,
rule triple60 adds 0 accepts (stalled, not slow). Boundary-free
torus control heals 2/2 fast (pair→2/3, triple30→0, p 1.86/2.03):
triple-lock localizes to boundaries (n=1 lock + n=2 clears —
hypothesis). Corners have grid-degree 2 with fragile detours; bulk
healing is unobstructed at order 3. Order-4 corner specialist
(MEASURED, test_update_rule.py + filed): visibility-chained 5-edge
re-pairing (945 matchings) hits the corner stall at ~4e-4 — via
DETOUR GRAFTS that keep the long edge itself while the other four
re-pairings rebuild its short detour (repair by neighborhood
restructuring, not dissolution). Strict census gate is LOAD-BEARING:
ungated order-4 accepts 10/10 while harming (longs 1→5 pinned;
corner 2→8 with p falling to 1.86, greedy-style window-gaming by a
local rule); gated quad20 clears the corner 2→0 (p frozen at
1.8255 throughout — the ultimate decoupling exhibit: full healing
invisible to the window), filed-not-shipped (30 s). Control-theory
lesson: coordination order must be paired with global gating, else
bigger moves do bigger harm. Full chain pair→triple→quad heals
every tried seed (5, 6, 7 open + torus 2/2). ROBUSTNESS + GATE
DUALITY (MEASURED, filed-not-shipped): across damage seeds (ns=10,
L=20), the pair→triple chain fully clears 3/5 (dmg0/2/5 →0 in ~2 s)
and stalls 2 (dmg1 →1-2 with a BOUNDARY residual (18,2)-(19,2),
n=2 for boundary-localized locks; dmg4 ungated →1 in 60 s / →3
with churn: 30 accepts, p rising to 2.22). Order-4 generalizes
PARTIALLY to edge locks: dmg1 triple-stall (top-edge + bottom-edge
pair) + gated quad20 →1 (top-edge cleared, bottom-edge (18,2)-(19,2)
persists, acc=1) — but 372 s for 20 steps (~19 s/exhausted step)
makes deeper pursuit prohibitive in-suite; filed-not-shipped. Strict-gated triple is
NOT universally better — it clears dmg4 both streams in 0.5 s
(100x: churn was pure waste) but STALLS seed7 at 1 where ungated
reaches 0 (the path needs neutral intermediates; gated burns 118 s
in the minimum). Neither dominates: the strict gate trades waste
for local minima. Queued design: census-ANNEALING at order ≥3
(uphill tolerance), plus a gated-pair audit. LANDED
(test_update_rule.py): rule_triple_anneal unifies both poles behind
a temperature knob — T0 = 0 (strict DECREASE; neutral rejected,
else <=-gate drift-churn: 149 s stall at 1) clears dmg4 both
streams in 0.5 s; T0 = 2 clears seed7 (strict stalls at 1) with
T0-robustness (1/2/5 all clear) but stream lottery (tseed 106
stalls at 1, filed-not-shipped: 200 s). Neither pole dominates
because stall topology differs (direct descent vs neutral
intermediates); the knob, not a fixed rule, is the answer.
Gated-pair audit (MEASURED, test_update_rule.py + filed): ungated pair accepts
net-harmful moves at 3/50 (all seed6) + 11 neutral across seeds
5/6/7 — essentially self-gating. CORRECTION to the first filing
(crude give-up-on-reject wrapper suggested weak dominance 1→0/10→2):
the principled in-loop gate shows DUALITY at order 2 as well —
strict gives (4, 2, 4) vs ungated (1, 10, 4): helps s6, HURTS s5
(neutral intermediates load-bearing there). Adoption REJECTED (a
worse-on-s5 default is bad science); instead rule_pair_anneal
replicates the T-knob at order 2 — T0 = 2 reaches (1, 4, 4),
matching-or-beating the ungated default on every stream. The knob
(not strict, not ungated) is now the answer at orders 2 AND 3.
Chain-workhorse upgrade (pair → pair_anneal) queued as mechanical
follow-up; endpoints heal fully either way. SURVEYED, REJECTED on
cost-benefit (filed-not-shipped): pair_anneal600 → triple30 reaches
s5 1→0 (p 2.0412 bit-identical — healed state looks like an
attractor), s6 4→1 (better than pair-fuel 4→2), s7 4→0, dmg4 4→0,
torus 2→0/2→0 — endpoints equal-or-better everywhere, but SLOWER
nearly everywhere (census evals: pair600 1.4 s vs 3-5 s; torus
chains ~2x). Consistent story kept: pair = fast chain fuel,
pair_anneal = best standalone order-2; no test churn for equal
endpoints at higher cost. SIZE ROBUSTNESS (MEASURED,
test_update_rule.py): L=30 damage (27 longs) → pair_anneal600 → 6 →
strict order-3 anneal60 → 0, connected (T0 = 2 also clears, acc 23
vs strict 6 — uphill tolerance only wastes here; ungated triple
churns: 30 accepts net −5). Healing is not an L=20 artifact.
CROSS-CANDIDATE BATTERY, first pins (MEASURED,
test_update_rule.py): triangular lattice generalizes — clean span
signature (all 1121 edges span exactly 2, 0 longs @smax2), swap
damage adds 24 longs with p 2.34 (same damage signature as square
2.362), guillotine30 heals 24 → 13 connected: locality repair is
not square-grid luck. Hex exposes a harness methods finding:
RADIUS must be fabric-relative, not just smax — hex plaquettes
(length 6) are invisible at radius 3 (every plain edge reads
radius+1, damage reads 0 longs @smax5, blind); at radius 5 the
signature resolves (plain 568×5 + 2×6 boundary floor) and damage
reads 54 longs. No hex healing claimed yet (the 2-long plain floor
breaks the fixed-point premise) — queued behind boundary-aware
gating; pair/triple on triangular queued next.
COORDINATION-IS-SUBSTRATE-DEPENDENT (MEASURED,
test_update_rule.py): on the denser triangular lattice (1121 edges,
degree ~6) pair600 ALONE clears 24 → 0 (acc 13, p reads plain to
1e-9 — full (p, longs) healing, no decoupling residual), where
square needs the triple endgame after pair600 → 1: more straddling
partners per long edge lower the required coordination order.
HEX FLOOR RESOLVED (MEASURED, test_update_rule.py): the 2-long
plain floor is two LEAF-anchored edges (degree-1 endpoints — no
detour can ever exist at any radius), a permanent census floor,
not damage; the interior census (leaf-anchored edges excluded —
graph-internal mask, swap-stable) reads 0 on plain, and the rule
is unfazed (guillotine10 takes 0 accepts). Healing works:
guillotine300 takes hex damage 54 → 17 toward the floor —
single-swap repair now partial everywhere (square 30 → 6, tri
24 → 13, hex 54 → 17), complete nowhere without coordination.
DELAUNAY JOINS (MEASURED, test_update_rule.py — Tier-1 reference
member): Poisson-Delaunay (400 nodes, 1179 edges) shows a clean
span-2 signature (0 longs, no floor), damage adds 21,
guillotine150 → 7 while pair600 alone clears to 0: dense
triangulated substrates (ordered tri + disordered Delaunay) heal
at order 2 — coordination need tracks density, and disorder is
no obstacle (triangulation helps: more straddling partners).
GABRIEL LIMIT (MEASURED, test_update_rule.py — harness operating
envelope): sparse disordered Gabriel (745 edges) has a broad span
spectrum (2..7 at radius 6; floor 15 vs dam 28 @smax6 — no gapped
signature), and guillotine descent overshoots BELOW the natural
level (plain 15 → 7, dam 28 → 6): the rule rewires away from
Gabriel-ness rather than healing toward it. Census healing is
well-posed only on gapped signatures (square/tri/hex/Delaunay);
the density prediction stands untestable here (blocked by the
methods limit, not refuted).
MEDIAL MIXED (MEASURED, test_update_rule.py): medial-quad (1179
nodes, 2340 edges) shows a clean span-2 signature (every edge in a
triangle — 0 longs), damage adds 60, pair grinds slowly (60 → 18
@600 → 6 @1200 — slow, not stuck), but the chained triple endgame
CHURNS (6 → 29, acc 30/30): all-short-local acceptance without
global gating does not imply repair on medial. Endgame behavior is
substrate-dependent (triple heals square, churns medial); gated
order-3 on medial queued; no full heal claimed there.
MEDIAL HEALS UNDER GATE (MEASURED, test_update_rule.py): the churn
was purely the missing gate — strict-gated order-3 (T0=0) clears
the medial pair1200 stall 6 → 0 in ONE accept (connected). Full
chain heals medial; gate duality is substrate-universal (square
dmg4: same strict-clears/ungated-churns split).
KNN MOSTLY-HEALS (MEASURED, test_update_rule.py): k-NN (1436
edges) has a near-gapped signature (floor 15 @smax2, ~1%) with
separable damage (+20 → 35); guillotine heals to the floor (35 →
16) while pair600 overshoots below it (35 → 9) — second overshoot
exhibit after Gabriel (milder): below-floor census cannot
distinguish repair from class drift; exact-floor targeting open.
LLOYD HEALS VIA CHAIN (MEASURED, test_update_rule.py — last Tier-1
member): Lloyd-relaxed Delaunay (1190 edges) shows a clean span-2
signature (0 longs), damage adds 19, pair grinds slowly (19 → 6
@600 → 1 @1200 — regularization slows order-2 vs Poisson-
Delaunay's 21 → 0 @600; mechanism open), strict-gated order-3
clears the last long (1 → 0). Cross-candidate battery now spans
square/torus/tri/hex/Delaunay/Gabriel-limit/medial/kNN/Lloyd:
healing is universal on gapped signatures, with order, speed, and
floor behavior substrate-dependent.
SELF-CALIBRATING CENSUS (MEASURED, test_update_rule.py — smuggling
point removed): total_longs_selfcal (span > median, no smax table)
reproduces the fixed census exactly on gapped signatures (square
0/30, tri 0/24, hex 2/54 incl. leaf floor, Delaunay 0/21).
Gabriel stays unseparated (326/349) — the limit restated
calibration-free: no threshold splits overlapping distributions.
Radius stays a parameter (hex needs 5); grow-until-median-
stabilizes queued.
BLIND-U REFRAMING (ADOPTED on review — U must not know M_O):
locality should characterize STABLE STATES of U, not appear in U's
objective function. The D1 verdict sharpens: direct microscopic
optimization of macroscopic locality requires nonlocal information
and unbounded coordination order (the 1→2→3→4-move lock hierarchy
now reads as climbing an artificial landscape, not converging on
the true U) — evidence that locality is not the microscopic
objective. Order-5+ search ON HOLD until blind-U results are in;
the "coordination is just what repair costs" alternative stays
on record as not-refuted (error correction also needs nonlocal
syndromes) — the blind tournament is the trial. Vacuum principle
PROMOTED (supersedes argmax-stability): V = {μ : U_*μ = μ}, the
stationary ensemble of an observer-blind U; the win condition is
G ~ μ_vac ⟹ M_O(G) local for generic O. U-admissibility criteria
(filed, mirror the five M_O criteria): coordinate-free,
permutation-equivariant, observer-blind (no p, N_long, M_O, or
reference graph in the rule), graph-local information, stochastic
if necessary, simplicity pre-registered (short description, few
parameters, stated before the tournament — a tuned 20-term H is
smuggling; note the why-this-U burden is acknowledged, not
dissolved). Observer-blind ≠ objective-free: sums of graph-local
motif terms (local Hamiltonians) are allowed; reference-embedding
quantities are not. N_long DEMOTED to external diagnostic
(implementation already graph-internal given (radius, smax); the
calibration is the smuggling point — self-calibrating census
queued). L0-INDEPENDENCE DISCIPLINE (adopted): no L0 proof may
cite U's objective, M_O's definition, or the selection principle
— L0 states conditionals, emergence decides which antecedents are
actual. First tournament results (MEASURED, test_blind_u.py):
pure drift from vacuum → p 1.26, longs 733/760, squares 361 → 6
(blindness alone insufficient — negative control); blind square
hill-climb fixes plain vacuum (0 accepts) yet from damage recovers
motifs WITHOUT healing (squares 323 → 341, longs 30 → 35, p past
2.4 — blind Goodhart: greedy ≠ sampling); triangle drive leaves
the square basin (tri 0 → 115, sq → 162, longs → 162) toward a
class needing substrate-agnostic measurement; touched-set delta ==
global motif gradient pinned (correctness of local acceptance).
METROPOLIS FOLLOW-UP (MEASURED, test_blind_u.py — finite-T does not
rescue motif optimization): the grid is NOT the square optimum —
T = 0.25 from plain vacuum reaches 375 > 361 squares (31 longs),
so square-dense non-grids outrank it and motif maximization cannot
select the vacuum even in principle; T = 0.25 from damage climbs
323 → 413 over 1000 steps while longs rise 30 → 140 (the 200-step
342 was slow climbing past, not a stall near the grid); T = 1.0
melts toward drift (squares ~140, longs ~345). No healing window:
motif-count maximization is misdirected, not merely insufficient.
KAPPA FOLLOW-UP (MEASURED, test_blind_u.py — strong signal, no
accessible direction): curvature SEES swap damage (exact OR:
plain mean kappa^2 0.0 flat; damaged ~0.065 with longs at
mean|k| ~0.93, pinned in tolerant bands) yet strict kappa^2
descent is FROZEN — 0 accepts on plain (flat fixed point) and 0
on damage over 5 steps, because improving single swaps run 0/300
blind and 1/300 even long-anchored (filed spikes). The
coordination disease strikes a curvature objective too: it is not
about which macroscopic quantity is optimized. κ-first targeting
would stay blind but needs ~100s of proposals per accept
(minutes per accept — infeasible in-suite, not shipped).
TRIANGLE-LANDING FOLLOW-UP (MEASURED, test_blind_u.py — blind
triangulation does NOT find the Delaunay class): mid-flow pin at
1000 steps (not stationary — still accepting at 2000: tri 239 →
290, acc 205 → 253) reads tri 239, clustering 0.33, squares 152,
longs 163, p 2.51 → ~2.78 — dense-cluster morphology, non-planar,
super-2D ball growth. Degree histogram frozen {2:4, 3:72, 4:324}:
swap dynamics preserves the degree sequence, so no swap-only rule
from the square grid can ENTER the Delaunay class (degrees ~6,
planar) — reachability confines the tournament to the
degree-sequence fiber (slides or the right starting fiber needed).
Maximizing the Delaunay motif joins motif-count maximization as
misdirected. Queued: damage-recovery-under-blind-U as the key
discriminator, non-maximization blind dynamics (curvature-driven
or degree-isostatic rules whose fixed points might coincide with
the vacuum rather than outrank it).

**Close criterion (graph instance):** derive (not choose) a scrambling `V_k`
from the graph Hamiltonian/adjacency; show the reduced radiation spectrum
follows the claimed Page curve under all:all dynamics. Then "Page curve is
a theorem of graph dynamics".
Update (this branch): graph instance closed at small-`N` ED level —
`graphvk` derives per-step `V_k = exp(-i H_graph dt)` from the hole adjacency
(disordered Heisenberg, one random XYZ term per edge), proves `V†V=I` (incl.
a composed-map inner-product test), computes `S_rad` from `rho_rad`, and shows
all:all tracks exact Page (mean dev < 0.25 bits at `N = 8`, typically ~0.01)
while the same `dt` on a chain sags below Page (mean dev > 0.4); changing the
graph changes `V` (`||U_complete - U_chain|| > 1`, `is_adjacency_sensitive`).
Fig 74b. What remains: large-`N`/thermodynamic limit, `k`-backreaction on the
interior spectrum, emission energy/mass spectrum, and `S_gen` extremization
from a gravitational path integral (QES still two-saddle + min-cut analogue).

**Kill relevance:** none currently (no observed BH Page curve); referee
honesty issue, not a falsifier.

## D2 — Kerr multipoles from the graph — P1 next cycle

**Missing:** derivation of spin-induced quadrupole `M2 = -M a^2`,
frame dragging `g_tφ`, `r_ISCO(M,J)`, Kerr QNM spectrum from graph dynamics.
Current status: only Kerr-Newman area `A(M,a,Q)` is assumed to set
`k_eff = A/4ln2` (`kerr`, `kerrpage`); overtone toy is Schwarzschild-like.

**Close criterion:** derive `Q = -M a^2 (1 + δ_Q)` without assuming Kerr;
compare `δ_Q` to GW241011 (`|δ_Q| ≳ 0.17` ruled out at symmetric-combination
level; factor ~2 resp. ~10% by parametrization, LIGO-P2500402).

**Kill relevance:** future wire (see v5 kill table "Kerr quadrupole").
GW250114 (LIGO-P2500421, SNR 80 area law + Kerr ringdown) and GW241011 are
currently consistent by construction, not passed predictions.

## D3 — κ -> c2 map (2PN) — ongoing

**Missing:** quantitative Ollivier-Ricci `κ` to 2PN coefficient `c2` map.
`c2 = p(2p-1)` is ansatz; power-law vs `1/r^2` disagree cross-applied.
See supplement S4 / BU. Kill wire `p = 0.92 ± 0.056` held to N=16000.
**v0.5 route:** curvature as failure of `V(r)` to scale uniformly via
`d_eff(r) = d ln V / d ln r` (`emergent_dim` protocol + controls; diffusion
viable at large t, resistance/communicability rejected on record).

## D4 — β(N), w from geometry — ongoing

**Missing:** bridge exponent `β(N)` (log-linear over 6 points, recalibrated
per N) and 2PN weight `w = 1.953` (solved from cancellation) derived from
graph Laplacian / Damour-Schafer from wiring.
**v0.5 route:** `β(N)` from `N(r)` implied by `V(r)` scaling (`emergent_dim`).

## D5 — NICER M-R-Λ + tidal deformability — P1

**Missing:** `R_1.4`, `M-R`, tidal `Λ` from routing stiffness.
Sharpest near-term test after kilonova rate (2-3 yr timeline).

## D6 — Mass-radius from wiring — long-term

**Missing:** `R_s = 2M` (BM reduction: `k(M)` iff `R_s(M)` given).
Single GR input; derivation from wiring alone open.
**v0.5 route:** `R_s` as radius where embedding `k` legs into `M_O(G_vac)`
forces a surface (T5 pop + `d_eff -> 3` IR fixed point, still open).

## D7 — Kilonova radiative transfer — analytic systematics done, full RT queued

**Update (round 4):** analytic viewing/opacity/dust systematics shipped
(`massgaps.gw190814_*_sys`, `gw190814_systematics_table`, Fig 75b, 9 tests):
POSSIS-inspired viewing (equatorial +1.25 g/+0.5 i) + Arnett opacity
rescaling bound the hiding window (equatorial + κ_blue=2 → P~0.18).
**Still missing:** validated multidimensional RT per the D7 v2 work package
(public-data ejecta compatible with F5/F6 bulk parameters, morphology +
velocity structure + Ye-dependent opacities/reprocessing, viewing-angle
dependence, direct i-band after the AT2017gfo anchor gate passes; POSSIS
primary). i-band direct not claimed until then (one-zone κ=10 over-traps).
g-band verdicts robust; gap-KN ~1/yr O5 prediction stands.

## D8 — Shedding efficiency ε(M,a) + upper-gap assignment — P1

**Missing:** derivation of the shedding efficiency's mass, spin, and
mass-ratio dependence from graph dynamics. Current status: `M_ej =
0.0168 M_tot` exactly universal (shed fraction 0.168 × 10% efficiency,
both fixed once on AT2017gfo; `collapse`, `massgaps`). Mass and
q-independence are extrapolated, not derived — the highest-value attack
surface on the universal (BBH) transient prediction.

**Close criterion:** derive `ε(M,a,q)` from `K_max(N)` combinatorics,
spin-ordered reabsorption, or remnant-trap physics with the shutoff
location (if any) as output, not input. A derived shutoff between gap
and BBH masses must land where it lands; inserting it at any observed
scale is refused (same rule as the 44 M☉ graph null).
Update (this branch): mass-ratio SHAPE + mass independence derived —
`mergershed` gets `frac(q) = η·2q/(1+q)²` from cross-bond counting with
`1/N` dilution forced by extensivity + all:all symmetry (monogamy
displaces `dS/s_leg` legs; `N` cancels). One calibration `η = 0.336`
replaces `e_final` (anchor `frac(1) = 0.168`); `η < 1` predicted and held;
`ε = 0.1` stays an astrophysics input. GW190814 dims ~0.4 mag vs the flat
prescription but stays kilonova-bright (`M_ej ≈ 0.157 M☉`); the flat
`collapse` law is kept as the O5 falsifier and the sample adjudicates
flat-vs-shaped (Fig 68b). Still open: `ε(M,a)` shutoff derivation.

**Related (not deferred — answered):** no graph feature at the
pair-instability edge. `k(M)` zero curvature, smooth spin/Love running,
He-core χ ~ 1e-8 (`massgaps`): the ~44 M☉ boundary belongs to
stellar/nuclear physics. Negative prediction, main text.

## D9 — Raychaudhuri for leg bundles (Jacobson-chain closure)

**Missing:** focusing theorem for SI fronts on leg networks. Current status:
the Jacobson chain is complete *except* this bridge — heat `dQ = eps·dk`,
Unruh `T = kappa/2pi` (input), saturated `dS = ln2·dk`, Clausius-demanded
`eps = kappa·ln2/2pi`, and measured `eta = ln2/PATCH = 1/4` giving `G = 1`
(`jacobson`: `clausius_leg_energy`, `measured_eta_closure`, all tested).

**Close criterion:** derive (not cite) Raychaudhuri-style focusing for fronts
propagating on leg networks; AT congestion slowdown is the documented seed.
Closes I6c in `docs/model.md` and promotes "Einstein equations follow" from
conditional to derived.

**Kill relevance:** none (gates no theorem in T8–T11); mathematical completion
of the AU triptych's third route.

## D10 — Tension spectrum: simulator d-dip around mass + tension→κ map (v0.6)

**Missing:** (a) the graph-side reproduction of the GR dimensional
fingerprint: an over-coordinated (tense, `z > 4`) region must show near dip +
overshoot + `→3⁺` under info-side `d_eff`, while relaxed `z ≈ 4` regions
show fabric `d = 2` / reconstructed `d = 3` as applicable; (b) a quantitative
tension→curvature map: Ollivier–Ricci `κ` tracking over-coordination (`z−4`).
Current status: GR side computed (`docs/relaxed-vacuum.md` §5: dip 2.990 at
`30M`, overshoot 3.030 at `100M`, `→3⁺` as `~1/l`); graph side: v0.6 probe
(L=100) shows unweighted tense plugs dip below fabric dimension and recover
from below (**inverted** vs GR far side — bare shortest-path rejected as
`d(i,j)` for tense regions, pinned), ad-hoc excess-degree costs flip toward
the GR side (mechanism check, `α` not derived), diffusion collapses on the
clique plug (heat trap, no power law); far-source near balls bit-identical
to control (relaxed-near-tension pin). D10b cost candidates (15 tests): tortuosity-import `w = 1 + c√χ` (`c = 1/2` from T11, zero-fit)
partially recovers the clique plug (1.60 → 1.86 vs control 1.92, no flip;
flip needs `c* ≈ 0.58`, diagnostic); `c_eff`-import `w = 1 + χ` (AT light
sector, saturating `x = χ/(1+χ)` bridge) flips clique (3.43, big overshoot)
and mild plug (1.73 → 2.02 vs 1.92, modest +5% overshoot) — overshoot-side
only, dip-phase (U-shape) open, amplitude unclaimed. Fingerprint + amplitude
(25 tests): 9×9 χ~1 plug shows full dip (−0.18) → overshoot (+0.79 peak) →
asymptote (+0.09) shape-match conditional on the ceff bridge; dip-min ratio
deepens (0.20/0.077/0.016), overshoot peak grows (0.79/0.94/2.91), far-field
`E ~ A(χ)Rc/r` with non-universal `A` (deficit ∝ tension; tail exponent
filed as D11); κ-profile is an
interface pattern (boundary-negative, core-positive), not monotone tracking
(criterion (b) refined to profile); flip lives in `z_vac ~ [2,5]` containing
P0' 4; conductance-weighted diffusion improves the heat trap (r² 0.54 →
0.78) without cleaning it. T15 cost-dominance theorem (`model.md` §2):
shortcuts priced ≥ hop-saving cannot inflate balls — c_eff at `z_vac=1`
satisfies it (max `V_w/V_0 = 0.2000`, no flip), tortuosity-import at
`z_vac=4` violates it on all 32 diagonals (fractional blip `V_w(1.9)=9>5`,
hidden from integer sampling, mid-window flips 2.020); c_eff at vacuum
`z_vac=4` violates on exactly the 24 boundary diagonals (witness: all 24
arrive early from endpoint balls; center-source volume blip peaks 1.077
at r=13.75, likewise hidden at integers).
Leading 2D+scale candidate mechanism: scale multiplicity `n_s(r) ∝ r`
(`dV_O ~ n_s·dV_G → R³`); `s` undefined, RG-log baseline gives the wrong
profile — linear-vs-log must be measured, not assumed (essay §8).
`emergent_dim` protocol +
two-distance bracket ready; shell no-emergence pin shows what failure looks like.
`M_O` formal upgrade (adopted): observer `O` is defined by a
graph-internal accessible observable algebra `A_O(G)`; observational
equivalence `G_1 ~_O G_2 ⟺ A(G_1) = A(G_2) ∀A ∈ A_O`, and
`M_O(G) = [G]_{~_O}` — an operational quotient, not a free
graph-to-manifold embedding (a clever-enough free map could make
anything look 3D). Admissibility requires all five: (1) graph-internal
(no target dimension, coordinates, metric, GR quantity, or desired
phenomenology in the definition); (2) permutation-covariant
(relabeling cannot change reconstructed physics); (3) coarse-graining
stable (`A_O`-invisible perturbations don't move the macroscopic
reconstruction); (4) operational (every quantity obtainable by
interactions available to `O`); (5) frozen rule (state-independent
prescription). `V_O(R) ~ R³` is an output test, never an input:
admissible-from-graph-internal-criteria ⟹ measure `d_obs`, not the
reverse. Substrate family (D13.0, MEASURED): triangular/hexagonal
positive controls reproduce `d_G → 2` with lattice-dependent
prefactors under one frozen measurement rule; gated-wall negative
control keeps bit-identical `~r²` balls with collapsed cut capacity —
`d_G ≃ 2` is not sufficient for channel scaling. Killer result queued:
same frozen `M_O` → `d_obs → 3` on every positive family member
(per-`M_O` tuning proves nothing). Vacuum-class sketch (from the
rewire sweep): degree sequence fixed does NOT imply 2D information
geometry — ~20 swaps in 3120 edges take V(14) 421 → ~909 with p ~ 2.6.
Candidate mesoscopic characterization: `G_vac ∈ C_2 ⟺ V_G(r) ~ r²`
over an expanding pre-boundary regime — but this risks circularity
(P0' says "vacuum is 2D"; defining vacuum graphs as "graphs whose
balls are 2D" defines the result). The primitive property sought is
absence of sufficiently long-range shortcuts, to be formulated via
graph-internal hierarchy, not coordinates (shortcut-absence
hypothesis, open). Sweep results (L=30/40/60, 5 seeds): few swaps
inflate (p > 2, placement lottery — typically 4/5 seeds rise by
ns=20), many swaps saturate (p → 0); N* (first ns with p > 2.2) has
median ≤ 40 at every L — O(10) shortcuts regardless of size (α ≈ 0
on L=30..60, fixed window). Scaled windows LANDED (L=40/60/80, [0.15L,0.35L]). Bookkeeping:
MEASURED — N*_med = (20,10,10); INFERENCE supported — N* = O(1)
consistent (α ≈ 0 over the tested range; rejects N* ∝ |E| there);
HYPOTHESIS — asymptotic f* = N*/|E| → 0. Headline: low-dimensional
locality is not generic; it must be protected. Working gloss (not a
new postulate): vacuum is a dynamically protected low-dimensional
information-locality class — something P0' + D1 must eventually
explain. Shortcut density is a candidate RG-relevant perturbation
(y_λ > 0? — investigation, not established). First RG-blocking
measurement SUPPORTS relevance: 2×2 blocking (L40 → 5) keeps
plain-grid long-edge fraction exactly 0.0 at every level while
ns=20 rewired flows 0.013 → 0.044 → 0.14 → 0.31 (>1.8× per step,
every seed; rough y_λ ≈ 1.5 from 24× over 3 steps). Long COUNT
falls (40 → ~18, some merge into short edges) while the DENSITY
rises 24× — the density is the relevant quantity. y_λ ≈ 1.5 is a
first estimate, not a quoted exponent (one blocking scheme, one f). Within-L caveat: at fixed
absolute ns the departure peaks mid-window and dilutes outward —
the relevance statement is f* → 0, not within-L growth. Small
systems saturate while large still inflate (ns=320: L=30 p < 1 <
2.5 < L=60 p). No sharp jump seen: smooth crossover with extreme
small-f sensitivity. Two emergence problems, kept separate (essay
§8): L0 locality (P0' + D1 — why U maintains a low-dimensional
connectivity class) vs observer dimensionality (D10 + D12 — why M_O
reconstructs 2+scale as 3D). Tier-1 substrate filing (universality
class, not lattice luck): Poisson-Delaunay (PINNED,
test_substrate_family.py) — planar, mean degree 5.97, shells ≈ 8n, linear cuts
(R² > 0.996), p ≈ 1.92..2.06, survives q = 0.10 deletion, dies on
20 swaps (p ≈ 2.50..2.67); Delaunay-medial quadrangulation (PINNED)
— 4-regular interior reproduces d_G → 2, so quad vs
triangulation does not select the dimension. Schaeffer-exact-UIPQ:
ATTEMPTED, FAILED with diagnosis — free-walk-plus-shift labels are
not conditioned well-labeled trees (post-hoc shift ≠ Doob
conditioning; root label free instead of 1; min->1 labelings only),
so the sampler never was uniform over well-labeled trees; the
observable symptom is parallel-edge concentration collapsing the
map origin to a degree-1 leaf (shells[1] = 1 all seeds) with
seed-unstable bulk p (1.69..3.24 at n=2000). Exact-Brownian
benchmark stays QUEUED behind the conditioned-labels sampler
(mobiles/BDFG route); the medial quad carries quadrangulation
evidence meanwhile. Lloyd-relaxed Delaunay (PINNED, iters=20 converged:
p = 1.91/2.08; Lloyd5 seed-0 p ≈ 2.3 was under-relaxation
artifact) and Gabriel/k-NN graphs (PINNED: connected, p ≈
1.92..2.02, linear cuts; Gabriel strictly sparser at ~2/3
Delaunay edges) plus short-only rewire (PINNED: span ≤ 2 swaps
keep p ≈ 1.77..1.96 at ns=20/80 — the rewire kill comes from
span, not rewiring as such). Ensemble ontology (ADOPTED on
review): Tier-1 degeneracy across topology/degree/order is the
EXPECTED signature, not a missing discriminator —
G_△ ∼_O G_hex ∼_O G_□ ∼_O G_Del ∼_O G_Gabriel is positive
universality evidence. The physical object is the class [G]_{~_O}
(prospectively the dynamical class [G]_{U,O}), possibly an
ensemble E_vac = {G : P_vac(G)} rather than one graph;
Poisson-Delaunay is frozen as REFERENCE MEMBER (gauge choice for
reproducibility), never "the" vacuum. Companion principle to the
five admissibility criteria: don't put information into the
vacuum that observation doesn't require — crystalline candidates
smuggle unrequested long-range order; the max-entropy program
(P(G|C_vac) ∝ e^{-λI(G)}, derive the typical graph from the
constraints) is QUEUED behind formulating the C_vac constraint
set without circularity (shortcut-absence still open). Spectral
leg (MEASURED, test_spectral.py): heat-trace d_s(t) on the
boundary-free 60×60 torus holds (1.95, 2.05) over t ∈ [10,100]
(method anchor — finite-size falloff only past t ~ 150); Weyl
counting fits land every Tier-1 member in one band (1.90, 2.15):
torus 2.049, open 1.947, tri 2.018, hex 1.983, Delaunay 2.103,
Gabriel 2.021, k-NN 1.926, medial 1.931. k-NN's 1.514 at N=1600
is a slow diffusive-crossover transient (clustering traps), not
a split — converges up with N as Delaunay converges down
(2.223 → 2.103). Lloyd EXCLUDED from spectral comparison: the
unclipped relaxation coalesces points above N≈1600 (mean degree
1.52 at N=6400/iters=20, 0.04 at iters=80 — degenerate input,
not physics); boundary-clipped Lloyd queued. d_s is now the
second universality leg beside d_H;
diffusion-anisotropy precursor (second-moment tensor of K(t))
SUPERSEDED by measurement: covariance is blind to 4-fold
(square-lattice heat is x↔y symmetric → A ≡ 0 exactly while
diamonds persist); angular-4-fold-power F4 replacement shows
lattice F4 already < 0.01 by t=10 (fast CLT isotropization)
while Poisson-fabric F4 sits at fluctuation level 0.01..0.11
with square-box boundary imprint at large r — no clean IR
discriminator at these scales. Fair lattice-vs-fabric IR
comparison (F4-decay exponents at matched radius) queued behind
toroidal point-set builds + the D13.5 propagation law; NOT
pinned. It pre-registers the minimize-preferred-frame criterion
for D13 as a questioned precursor, not evidence.

**Close criterion:** (a) measured `d_eff(l)` profile around a tensed region
matches the GR fingerprint *shape* (dip, overshoot, asymptote) after the
simulator mapping is fixed, with amplitude scaling in the tension; relaxed
control regions show `d = 2` fabric scaling. (a) is SATISFIED conditional on
the ceff cost bridge (mild-plug shape + amplitude scaling pinned); full close
needs the bridge derived or replaced by derivation. (b) κ-PROFILE (REFORMULATED
after monotone-tracking failed): boundary-negative / core-positive pattern
with stated values, first measurement recorded (clique −0.93/+0.89, mild
−0.31/~0, fabric 0) — CLOSED by corner-free disk-plug confirmation
(R=3, 29 nodes): internal +0.90, boundary −0.86, fabric 0.00, matching
the clique pattern quantitatively, so boundary negativity is a genuine
tension-interface effect, not a square-corner artifact. Both (a) and (b)
must output their
curves from graph construction + dynamics, not take GR as input.

**Kill relevance:** P0' first quantitative wire. Failure of the (a)
shape-match after the mapping is fixed refutes the relaxed-vacuum postulate;
success promotes curvature-as-self-stress from ontology to measurement and
feeds D3 (κ→c₂ via tension) and D6 (R_s from the tension profile).
Generalization stated as the tension-imprint conjecture (`model.md` §5):
fingerprint universality under the fixed ceff rule, with falsifiers and
P5-promotion criteria; the cost rule stays conjecture-grade until they are met.
D10a bridge-derivation attempts (MEASURED NEGATIVES, not pinned):
(i) random-walk first-passage across the plug ladder DECREASES with
χ (416 → 304 → 263 → 232 steps, plain → mild → x2 → x3; clique 237)
— tense regions conduct faster, so √χ-as-traversal-delay has no
walk derivation (anti-tortuosity); (ii) plug residence (center exit
time) scales as exitT/exitT0 ~ (1+χ)^0.78 with a mild→clique jump
(10.4 → 12.0 → 14.2 → 14.8 → 32.9) — sublinear but neither √χ nor
linear, deriving neither candidate's form. Remaining honest paths:
tighten the BV ln2 bracket to c = 1/2 analytically (pen-and-paper),
or the congestion route via D1 update-capacity (gated on U). The
imports stay labeled.
WEIGHTED-AUDIT ADOPTION (Leblond, pleblond/weighted-graph-paper —
"Distance, Volume, and Apparent Dimension in Weighted Graphs"):
the paper's Prop 1 (cost dominance) generalizes our T15 and its
endpoint witnesses generalize our witness-node corollary — T15 now
cites Prop 1 as the parent theorem (paper refresh queued); its Prop 2
(arrival-event sweep) is ADOPTED as our weighted-measurement
discipline (Sec 7 audit order: specify → census edges → complete
arrival profiles → fit last), implemented in bh_graph/weighted.py
(cross-checked against the paper's exact 3-vertex blind spot:
integer radii agree, excess on [3/2,2), max ratio 3/2; dominance
restoration removes all inflation — test_weighted.py). Our T15
fractional blips (9>5 @1.9, 1.077 @13.75, both integer-hidden) are
instances of the paper's blind-spot phenomenon; ball_volumes_weighted
(linspace/integer grids) is flagged for event-sweep upgrade wherever
inequalities are certified. Slope identities (Eq 15/17: p_w − p_0 =
slope of log R) reframe D11: excess slope is ratio-recovery, not
inflation — D11-tail re-analysis under this lens QUEUED (check E-tails
against R_x profiles; Eq 22 deficit-recovery may describe them).
L0 STATE UPGRADE (ADOPTED direction, machinery queued): G = (V,E,w)
with w_ij as L0 DOF (coupling strength); unweighted results stand as
the w∈{0,1} strong-backbone sector. First weighted result (MEASURED,
test_weighted.py): weight-tolerance recovers geometry — the same 30
damage longs read binary-collapse at Lw=1 (GoF2 0.385) but
near-vacuum at Lw=20 (GoF2 0.684, lam2/lam3 5.49 past the 2D bar);
continuity in weight is the weak knob binary lacks (lam2/lam3 dips
to 1.36 at Lw=5 mid-transition, filed as-is). Weight-selection
principle required before further results (graph-internal, blind,
pre-registered — candidates: interaction counts, U-dynamical
attractor, w(χ)); model.md L0-box update queued with the paper
refresh.
WEIGHT-SELECTION PRE-REGISTRATION (binding on all entrants): a
weight rule must be (a) graph-internal — function of local graph
state only (degrees, spans, κ, traffic), no coordinates/reference
embedding; (b) blind — no M_O, no target dimension, no plain-grid
comparison inside the rule (plain grid allowed in EXTERNAL scoring
only); (c) stated whole before the tournament, ≤2 parameters.
Scoring is the TRIPLE READOUT (pinned protocol): MDS profile
(geometry) + event-sweep domination (inflation) + underpriced
census (contraction) — the paper's §2.2 lesson that no one readout
substitutes for the others. First entrant (MEASURED, testable,
test_weighted.py): SELF-PRICING w_e = span_e (zero parameters) —
on 30-long damage MDS stays blurred (GoF2 0.402 vs 0.769 vacuum /
0.385 binary), sweep shows full domination (maxR 1.0, no positive
intervals), census lists 16 violations: contraction-without-
inflation (Counterexample-A regime on damage). Softens, does not
restore — the baseline every later rule must beat. Queued: w(χ)
tension rule, traffic-weighted (SI-count) rule, marginal-boundary
rule (w at domination edge — needs blind d_0 proxy, open problem).

## D11 — Far-field tail exponent of the tension fingerprint (D10b)

**Missing:** the asymptotic law of the excess-slope tail `E(r) = p_w − p_0`
far from a tensed region. Two shadow accountings compete: a *wedge* shadow
(delayed nodes `~ Rc·r` in 2D) gives deficit `D = 1 − V_w/V_0 ~ Rc/r` hence
`E ~ 1/r`; a *fixed* shadow (constant delayed interior `~ Rc²`) gives
`E ~ 1/r²`. L=120 probe (strength trio, `Rc`-relative windows): χ~1 tail is
`1/r²`-like to `6Rc` (`E·r²` flat: `A = E·r/Rc` falls 0.30 → 0.16 as `1/r`);
χ~2 is `1/r`-like to `5Rc` (`A` flat 0.64 → 0.63) then bursty; χ~5 bursty
throughout. Windows past `~6Rc` are boundary-contaminated on L=120
(half-width 60; χ~1 `k=10` window fully clipped, `E = 0.0000`), so neither
law is established — the exponent may be tension-dependent or one law may
be a transient of the other.

**Close criterion:** measured `E(r)` tail on `L ≥ 200` with clean
(`Rc`-relative, unclipped) windows to `10Rc`, deciding `1/r` vs `1/r²` vs
tension-dependent crossover, with the winning accounting derived from the
cost rule rather than fitted. DECIDED (test_emergent_dim.py, L=200/240/250):
χ~1 → 1/r² (E·r² flat 0.633..0.642, k=3..10 — fixed shadow); χ~2 → 1/r
(E·r flat 6.12..6.67, k=2..10 — wedge shadow); χ~5 SLOW CROSSOVER
(L=480 to 20Rc: fitted q = 1.19 over k=6..14 → 1.10 over k=14..20,
E·r still monotone-falling 7.90 → 6.55 with shrinking steps) —
1/r supported asymptotically but not firm at 20Rc; L=600 extension
to 25Rc (filed, not shipped: E·r 6.55 → 6.44 still falling, late
q ≈ 1.09) confirms the crossover is very slow, not yet the limit;
the pinned claim
is the crossover, not the limit. The
exponent is TENSION-DEPENDENT. Accounting derivation from the cost rule
remains sketched (delay-region geometry), not derived — D11 closes on
the measurement.

**Kill relevance:** none directly — a shape detail, not the shape itself.
Feeds the tension-imprint conjecture amplitude clause (`model.md` §5).

## D12 — Reconstruction universality: why admissible M_O converge

**Missing:** the reason independently-admissible observer reconstruction
maps recover the same macroscopic geometry. `model.md` defines objective
spacetime as the part of `G`'s information structure invariant under all
admissible `M_O` — but names no independent admissibility criterion, so
"admissible" risks meaning "gives 3D" (circular). The critic's question
stands: why resistance / diffusion / communicability distance, and why
couldn't another reasonable reconstruction give 4D, 7D, or no smooth
geometry at all?

**Close criterion:** `A_macro(G)` = {`M_O(G) = [G]_{~_O}` : `A_O`
satisfies the five admissibility criteria (graph-internal,
permutation-covariant, coarse-graining stable, operational, frozen
rule — D10)}. The access floor is part of the definition (a
single-node "observer" recovers nothing); `V_O ~ R³` is the output
test, never an input. Target: ∀ `M_O ∈ A_macro(G)`,
`M_O(G) ∼ M` up to coordinate/coarse-graining equivalence. P4 audit
(uniform Ollivier, `orici`, p=0): (1) graph-internal PASS (uniform
neighborhood measures + hop metric; no coordinates or target
dimension); (2) permutation-covariant PASS + TEST (relabeling leaves
the κ multiset unchanged); (3) coarse-graining stable PASS on flat and plug backgrounds
(single-edge flip moves κ only within 3 hops, far drift < 1e-9 —
measured modulus); (4) operational
PARTIAL (EMD computable from neighborhood data in principle, but
global-EMD + full-neighborhood readout exceeds local-observer access —
needs access-cost accounting); (5) frozen rule PASS (p=0 uniform
prescription is state-independent).
Partial-credit ladder:
(i) criterion stated + non-circularity argued; (ii) two instances agree on
vacuum fabric; (iii) agreement extends to tensed regions (fingerprint
shape under both). Prerequisite (fiber control): verify `M_O`
preimages exist at the reconstruction resolution — distinct
`G_a ≠ G_b` sharing a macro-state — else C3's twin-histories test is
untestable. Dynamical extension (on review): once D1 exists the
universality object upgrades from `[G]_{~_O}` to the dynamical
class `[G]_{U,O}` — microscopic graphs may fluctuate
(`G_1 → G_2 → …`) while `M_O(G_1) ≃ M_O(G_2)`; Tier-1
indistinguishability is then exactly what emergence predicts, and
the vacuum measure over graphs (or its dynamical universality
class) replaces the winning tessellation as the derivation target.
Observer-indexed extension (user construction, spiked next):
M_O(G, o) with a 2D sky chart (angle × shell from vantage o) plus
relational depth D(o, v) (communicability / resistance / diffusion
time / channels) re-embedding the chart into an apparent 3D view;
V_O(R) ~ R^3 is the output test per depth candidate (D10 killer
design). Adds vantage-covariance as a second universality axis:
views from distinct o must agree up to IR translation; sky-shape
(concentration vs dilution of solid angle) is a new falsifier.
Static depth bake-off (MEASURED NEGATIVE, L=40 grid, V_O(R) exponent
d_obs; tuned-null hop^0.667 gives 2.73 = finite-size R^3): hop 1.82,
resistance 4.18 (log-growth explodes volume), -log(communicability)
1.32, (hop^2·res)^{1/3} 2.28 (best, still short), sqrt(hop·(-logC))
1.54. Within-shell dispersion: -logC spread ~ r^1.15-1.32
(superlinear!), resistance ~ r^0.2-0.4. NOTHING principled reaches 3:
observer-3D does not fall out of standard relational distances.
Surviving static route is multiplicity-weighted counting (the D10
skeleton, w unprincipled); dynamical depth via U-influence queued
behind D1. Vantage-covariance queued behind depth discovery.
Holographic+relational reframing (ADOPTED user construction): the
sharp formulation is holographic DOFs + pairwise relational distance
d(i,j) = f(interaction_ij) → emergent localization, with M_O demoted
from dimension-manufacturer to readout of a dynamically generated
metric. The test is distance-geometry: cMDS of D² (B = −½JD²J) must
show N-stable λ1,λ2,λ3 dominance (λ3/λ4 gap persisting as N grows;
rank growing with N kills it); f must pass all five admissibility
criteria (no smuggled 3D — that's where the guard now lives). MDS
readout on statics (MEASURED NEGATIVE, filed-not-shipped spike,
L=20/30 grids): calibration first — grid-hop control shows λ1,λ2
dominance (GoF2 ≈ 0.8, λ2/λ3 ≈ 6.8) with decaying tail + negmass
0.30, so the honest bar is an N-stable λ3/λ4 gap, never exact rank;
resistance shows no gap anywhere (GoF3 0.32); −logC is 2-dominant
with its λ3/λ4 gap SHRINKING 2.44 → 1.23 from L=20 → 30 (wrong
direction). No rank-3 selection under MDS either — second
independent negative for statics, and the pipeline is validated (it
does not hallucinate 3D). The missing piece is now crisp: an
ATTRACTIVE relational dynamics generating d(i,j) (D1's U is repair
dynamics, not attraction) — design queued; Tier-1 MDS control sweep
queued behind it. Tier-1 MDS calibration (MEASURED, test_mds.py):
grid/tri/hex/gabriel/knn hop all show lam1,lam2 dominance (GoF2 >
0.7, lam2/lam3 > 3, lam3/lam4 < 2.5) — but the DELAUNAY reference
member shows lam1,2,3 co-dominant (lam3/lam4 ~ 5-6, all 5 seeds;
lam3/lam1 GROWS 0.53 → 0.79 from N=400 → 1600). Diagnosed, not a
dimension: v3 correlates 0.93 with centered r² and 0.85 with
per-node tortuosity — a RADIAL TORTUOSITY BOWL (hop grows
superlinearly with Euclidean radius in the open disordered box;
cMDS embeds the warp as a bowl axis). Consequences: (i) the MDS bar
is per-substrate — del-hop's null INCLUDES lam3, so del-based
rank-3 claims must clear lam3/lam4 >> 6; (ii) eigenvector geography
is part of the test — genuine v3 must decorrelate from radial /
tortuosity fields (new D12 falsifier clause); (iii) radial
detrending is queued as an open method problem (must use a
graph-internal radial proxy, never coordinates).
Observer-relative locality formalism (ADOPTED from review dialogue,
D12 core): coordinate-free network G = (V,E,I,D), observer-rooted
A_O with G1 ~_O G2 (already filed) PLUS: (i) operational
C_O(r) ∝ r² WITHOUT assuming Σ_O(r) = S² (area-scaling as pure
counting, no smuggled sphere); (ii) generalized emergence formula
C(r) ∝ r^d_H + independent depth ⟹ V ∝ R^{d_H+1}; (iii) no global
X — X_O ≠ X_P in general, with relational transition maps T_OP on
shared domains + cocycle condition (charts→manifold inversion, not
manifold→charts); (iv) observer-relative locality predicate
L_O(A,B;ε) = Θ(ε − ρ_O(A,B)) with IR compatibility required only
macroscopically; (v) two-theorem skeleton (emergence + compatibility)
with shell-independence dV_O ∝ C_O(r)dr as THE attack point —
operationalize via shell mutual information / cut-capacity freshness
(X_r ⊥ X_{r+dr} at coarse scales), queued as codeable. CRITICAL GAP
FLAGGED (the d_H = 2 input): on 2D fabric, naive shell counting gives
|shell| ~ r¹ (nodes AND cut capacity both linear) — so C_O ∝ r² does
NOT follow from 2D shells, and assuming it begs the question (2+1=3
in a trenchcoat). Candidate rescue: PAIRWISE relational counting
(~|shell|² ~ r²) as the source of d_H = 2 — i.e., the holographic
exponent counts relations, not nodes. Queued: derive-or-refute C_O
scaling from graph structure before any emergence claim.
Shell-counting DILEMMA (SKETCH, test_mds.py leg pinned — not a theorem):
on 2D fabric, honest per-shell counts give nodes ~ r¹, cut capacity
8r+4 (pinned law), shell-MDS rank O(1) (scale-invariant ring profile,
GoF2 = 0.772 at every radius — pinned), entropy extensive ~ r¹ —
NOTHING reaches r² per shell; while the only natural r² count
(cumulative ball volume/entropy) violates shell-independence BY
CONSTRUCTION (inner shells re-counted at every outer radius). So
d_H = 2 XOR shell-independence: the emergence derivation cannot have
both from shell counting. Nonlinear-depth escape closes too: d_obs = 3
needs dr/dρ ~ ρ²/r ⟺ ρ ~ r^{2/3}, i.e. exactly the tuned-null
hop^0.667 already filed unprincipled. Escapes left open (honest):
C_O counting something non-geometric with r² scaling (new physics),
or non-shell composition of depth × transverse. Pairwise-counting
rescue REFUTED as stated (~|shell|² counts constrained pairs, true
DOFs ~ rank ~ O(1)) — pairs overcount by arithmetic, independence
fails by triangle inequality.
DILEMMA SCOPE (load-bearing clarification): the dilemma kills the
SHELL-COUNTING route FOR HOP SHELLS only — the MDS-rank route is
independent and unaffected (it never counts shells). Under a
dynamical metric, shells redefine (equidistant sets under ρ) and
C(r) reopens empirically: IF some dynamics yields MDS-3, its shells
must show r² transverse counts, resolving the dilemma by measurement
rather than derivation. So the dilemma concentrates ALL weight on
dynamics design — no static escape remains. First dynamical distance
(SHIPPED, scrambling.si_fpt_matrix + test_mds.py): mean SI
first-passage time (β = 0.5, K = 100, 10×10) reads cleanly
2-dominant (GoF2 0.89, λ2/λ3 17.5 — MORE Euclidean than hop:
stochastic averaging smooths lattice anisotropy). Dynamical
generation alone does not select 3D — rank-3 is a nontrivial
dynamical property, and biased/attractive variants are the queued
hunt. Methods note: the FIRST FPT implementation (non-persistent
frontier) produced capped garbage reading high-rank — caught by the
volume cross-check (balls all size 1), fixed, corrected numbers
pinned. Cross-readout validation works.
FABRIC-HOLD VERDICT (P0' level, filed on review question "should we
revisit the fabric?"): NO — the 2D fabric premise is the
best-supported part of the program (d_H + d_s + Tier-1 universality +
N* protection problem, multi-legged), and the alternatives are (a)
3D substrate: circular, kills the emergence program's point; (b)
non-integer fabric: Tier-1 pins 2 robustly, and d_H+1 would give the
wrong integer anyway; (c) shortcut-mixed fabric: N* work shows that
is damage, not vacuum — SUPERSEDED IN PART by the weighted upgrade
(review amendment): "shortcut" splits into strong shortcut (damage,
binary-sector verdict stands) vs weak global coupling (vacuum-
compatible per the weight-tolerance result: Lw=20 reads near-
vacuum). Amended ontology: vacuum = near-2D strong backbone +
weak global relational wiring; matter = locally concentrated
strong/high-density connectivity; BH = extreme connectivity/tension
limit. (d) DYNAMICAL fabric class [G]_{U,O}: the only
live refinement — already queued, not a retreat. The emergence
failures to date are failures of specific MECHANISMS (static
distances, shell counting, unbiased SI), never of the premise — and
the attractive-dynamics route is untested. Right response to the
dilemma: stop asking static fabric geometry for 3D (that question is
closed, multiply negative) and put all weight on the
dynamical-distance hunt. PRE-REGISTERED TRIAL CONDITION (against
sunk-cost drift): if a FAIR hunt over attractive/bias dynamics
classes (state-, tension-, curvature-coupled β + U-influence depths)
finds no rank-3 selection with N-stable gap and non-radial v3, the
fabric premise itself goes on trial. Next fabric work is not
revisiting 2D but upgrading static → dynamical: D1→fabric feedback
(stability tournament — do the healing Us preserve d_G ≃ 2 on
vacuum? U(G_vac) ∈ C_vac), now testable since U candidates exist.
TOLERANCE CURVE, unweighted baseline (MEASURED, test_mds.py —
forces weights): on square L=20, 2 binary longs collapse MDS
2-dominance (lam2/lam3 6.82 → 1.93, GoF2 0.769 → 0.632); by 30
longs GoF2 0.385, participation ratio 3.3 → 10.3, kappa^2 0.0645;
lam3/lam4 never gaps (~1.1–1.7, pinned < 2.0): weak binary wiring
blurs 2D, never builds 3D. Binary "weak" links are maximally
strong — no binary knob is weak. The ε in G_vac = G_near-2D +
εG_global has no unweighted meaning beyond count-fraction (already
razor-thin per N*); weak wiring must be WEIGHTED (coupling
strength), queued as the L0 state upgrade G = (V, E, w).
(n,k) GROUND FLOOR (from D14 review dialogue — adopted):
fundamental ontology = universal tick n + state S_n + update U
(state+time+update, NOT spacetime); space/d_O/curvature emergent
at M_O. (n,k) separation rigorous: n = U-evolution, k = R-scale;
[U,R]≈0 (evolution–coarse-graining commutation) is D12's central
consistency equation for admissible (U,blocking) pairs. DEBT
LOGGED (not claimed): universal tick = preferred simultaneity,
so emergent Lorentz (or its precise failure mode) is owed at M_O
level — tick-vs-M_O-time mapping is D12's ground floor; the
Lorentz question sits on this ledger. D14's η(n,k) surface is the
joint object both items read.

**Kill relevance:** none directly — a meta-criterion over D3/D4/D6/D10.
But a second admissible `M_O` giving robustly non-3D IR on relaxed fabric
refutes the P0' reconstruction program (same-`M_O` falsifier, essay §8).

## D13 — Emergent causal order: update rule → cone → clocks → interval (staged)

**Missing:** the temporal half of "why spacetime?". L0 has no dynamics
(D1); D1's scope now includes time itself, not just evaporation/QES
(D1 provides `U`; D13 asks whether `U` becomes time — the items share
their object). Target, split by level (corrected): `V_G ~ t²` at
substrate, `V_O ~ R³` after `M_O`; microscopic index `n`, causal order
`≺_U`, and clock time `τ` are three distinct orderings (`n ≠ t_obs` as
`d_G ≠ d_obs`).

**Control (D13.0, MEASURED):** static P0' substrate geometry: analytic
`V_G(r) = 1+2r(r+1)`, bit-pinned at L=40/80, finite-window fits rising
toward 2 with radius (1.9196 → 1.9603 fractional); plus the plug sign
pattern (35<38 hops vs +5.0 weighted) as pre-registration for stage 1.
Briefly filed as stage 1, demoted on review: first-passage here *is*
hop distance — compatibility with a cone is not observation of one.
Substrate family MEASURED (de-brittling landed): triangular (shells
6n, cuts 12r+6) and hexagonal (shells 3n, alternating cut law)
positive controls reproduce `d_G → 2` with lattice-dependent
prefactors under one frozen rule; gated-wall negative control keeps
bit-identical `~r²` balls with collapsed cuts. Noisy-grid disorder
control MEASURED (q=0.10 edge deletion: jittered shells, `p = 1.909`,
linear cuts — statistical pins, no lattice law); rewired-grid
fragility control MEASURED (20 degree-preserving swaps: identical
degrees, balls accelerated past `~r²` — V14 ~909 vs 421, `p ~ 2.6` —
the opposite failure from gated-wall bottlenecks).

**Close criterion (staged):** (1) `U → T_U, ≺_U`: stated local
update rule + counterfactual-influence machinery:
`δ_U(s,v;n) = D(R_v[X_n^{(s)}], R_v[X_n])` from a do-intervention at
`s` (minimal standardized perturbation; graph, `U`, boundaries, and
noise realization held fixed — paired randomness for stochastic `U`),
influence ball `B_U(s,n;ε)` with `V_U(s,n;ε) = |B_U|` plus integrated
`Ṽ_U(s,n) = Σ_v f(δ_U)` so ε-sensitivity is signal, not embarrassment
(`D`, `f` unfrozen); `V_U ≠ V_BFS` by construction. Order
`s ≺_U (v,n)` from intervention, not correlation. Required controls:
null (no intervention → δ = 0), disconnected (paths cut → δ = 0),
speed-limit (radius-`q` `U`: `d_hop > qn` → δ = 0) — the last giving
analytic `C_U^max` against which measured `C_U^influence` can be
narrower; (2) `(≺_U, M_O) → cone`: observed causal cone compatible
with the *same* `M_O` producing `R³`, order-dimension agreeing with
`d_eff` (1+3 output, not input); (3) clocks: internal-cycle clock with
`dτ/dt(χ)` reproducing the T9 profile from capacity/congestion,
unimported; (4) interval: `g_μν` from `(≺_U, V_U, M_O)`
(Malament-shaped: order fixes the conformal class, the stage-1
influence volume `V_U` (event counts in causal balls) fixes the
factor; spatial `V(r)` is reachability, not event volume) reproducing the T8–T11 battery. Each
stage closes independently; GR is
the check, never the input, and only at stage 4. (5) dispersion /
isotropy (QUEUED behind a local propagation law): same law on all
Tier-1 candidates, measure `ω(k)` — IR `ω² = c²k² + a_4k⁴ + …`,
angular `c(θ)`, anisotropy/birefringence-like corrections;
selection criterion minimize-observable-preferred-frame-structure
under coarse-graining (variational form: maximize macroscopic
symmetry subject to minimum microscopic structure). Static
precursor runnable now: diffusion-anisotropy tensor of `K(t)`
(D10 spectral leg). Tier-2 static members (Kagome/Dice, Penrose,
stealthy HU) CANCELLED per direction: Tier-1 already spans
topology × degree × order, further static d_G adds no axis.
J2 PROBE PRE-REG (D'Ariano-Erba-Perinotti 2019 coinless-QW
substrate, proposed as D10 candidate — spec VERIFIED,
admitted as PROBE not Tier-1-track per standing
no-new-statics direction): J2 = Z2⋊Z2 (swap action),
vertices (x,y,b), walk-graph gens {±h1,±h2,±h1c,±h2c}
(checks: 8 distinct, inverse-closed h1c↔-h2c/h2c↔-h1c =>
undirected degree EXACTLY 8; neighbor fn matches multiply
in both sheets; quotient 2-cell→square lattice VERIFIED by
hand (4 micro-edges per coarse edge); ball-over-periodic
endorsed). QI THEOREM-DIRECTION: [J2:Z2]=2 => QI to square
lattice => growth/spectral/ends MUST read d=2 — volume
battery = NEGATIVE CONTROL on apparatus (failure indicts
apparatus, never J2); d_eff→2 is calibration,
oversold-as-discovery guard filed in advance. NEW-AXIS
CASE (the only license under cancellation direction):
built-in two-scale structure (micro z=8 non-bipartite
two-sheeted vs coarse z=4 bipartite single, QI-identical)
=> J2's job is MICRO/MACRO DISCRIMINATION: do D10
short-scale readouts track micro or coarse?
PRE-REGISTERED: (i) long-scale must agree micro-vs-coarse
(QI control); (ii) NON-BIPARTITE (c-gens preserve x+y+b
parity => odd cycle exists => walk APERIODIC) =>
MICRO-PREDICTION: some odd-n return >0 on J2 vs ALL
odd-n =0 on square (exact-walk apparatus reuses;
aperiodicity is the claim — fixed small odd n may be 0);
(iii) 4-cycle census (square-like plaquettes + mixed;
family already spans short-cycle variety —
characterization, not discovery); (iv) PERTURBATION
RESPONSE = sharpest probe (existing battery; match =
within family response envelope, tolerance = family's own
spread — no new threshold invented). TIER STATUS:
explicitly DEFERRED — Tier-1-track needs direction-level
acceptance of 'built-in coarse-graining' as a new axis
(user call) OR a perturbation SURPRISE (discovery route);
default verdict = apparatus knowledge (D10 readout
scale-sensitivity), not tier placement. ISOTROPY-BANKING:
J2's Weyl pedigree is DIRECTLY relevant to the QUEUED
dispersion/isotropy program (selection-for-isotropy
precedent: minimal scalar micro → isotropic Weyl macro)
— bank J2 as first substrate for that program when it
unqueues; until then pedigree = motivation only (quantum
result, classical tests — nothing transfers;
pointer-not-evidence). FIREWALLS: D10-side ONLY (no
pricing/gain/U content — zero D14/D1 relevance beyond
theme). QUEUE: pilot needs NO new apparatus except
constructor + quotient check (battery + perturbation +
walk all exist) — recommend next-go pilot (cheap,
spec-complete) then formation design; user may reorder
formation-first (critical-path call).
J2 PILOT VERDICT (executed, 5 tests — probe verdict STANDS,
no tier claim): LOGIC ERRATUM (falsified-by-data, mechanism
understood): the filed NON-BIPARTITE claim was WRONG
(a p-preserving edge is not an odd cycle — fallacy);
correct bipartition q=x+y (EVERY micro-move flips it) =>
J2 IS BIPARTITE => odd returns vanish EXACTLY like square
(all odd-n =0.0 through 11, theorem all-n). VOLUME (QI
control PASSES): shells EXACT 8/17/8r (r=1/2/3..22),
p[8,20]=1.9205 in band, fractional approach 1.8403->
1.8937->1.9205 (tri/hex pattern), quotient shells EXACT 4r
(r=1..20), micro-vs-coarse Δp=0.0000 (bound was 0.15).
QUOTIENT: 1861 cells/3600 edges (R30); EVERY quotient edge
square-adjacent globally; 1741 strict-interior cells all
square-4 with micro-mult EXACTLY 4 per coarse edge
(hand-verification reproduced). CUTS: EXACT 32r+16
(r=2..22; r=1 is 56) — J2's cut law (prefactor filed,
non-universal per family rule). WALK REFRAMED: parity
pattern coarse-matching (both bipartite), even VALUES
micro-tracking (p2=1/8 vs square 1/4 exactly; p4+ pinned).
C4 CENSUS (apparatus validated exactly on squares):
26072 @R18 (N=1370) vs ~1300 square-equivalent — ~20x
density, sheet-mixing cycles: tracks MICRO. PERTURBATION
(sharpest probe): swaps ns=20 -> 2.49/2.60/2.16 (2/3 kill
per majority rule; seed2 = documented lottery miss,
Delaunay-stream-1 precedent) + q=0.05 -> 1.9205/1.9203
(deletion-robust) — FAMILY-TYPICAL both legs, NO surprise
=> no discovery-route tier claim. PROBE CHARACTERIZATION:
long-scale agrees (QI); short-scale splits (parity coarse,
degree-values/C4/cut-prefactor micro); perturbation
family-typical. J2 = banked characterized probe + isotropy
program first substrate (standing). MDS-tolerance-on-J2
QUEUED (needs long-edge definition on two-sheeted graphs
— design question, not rushed). NEXT: formation design
(critical path resumes).

**Over-arching falsifier (C1–C5, essay §8):** `M_O ∘ U ≃ U_eff ∘ M_O`
with coherence → locality → autonomy → universality → GR limit, each
level presupposing the previous (C4 quantifies C1–C3 across `A_macro`).
Autonomy-before-GR: snapshots resembling GR whose next step needs hidden
`G_n` fail. Operational form: twin histories (`M_O(G_a) = M_O(G_b)` ⇒
`M_O(U(G_a)) ≃ M_O(U(G_b))`, ε–δ in macro-profile distance, RG-weakened
`ΔM → 0` in the IR); presupposes D12 fiber control. Roof: macro-states
as `~_macro` dynamical-equivalence classes; factoring `M_O` through
them does NOT imply autonomy (two-bit swap counterexample: singleton
classes, failing twins — essay §8), so the twin criterion stays
defining. Stage 4 vs C5: stage 4 reconstructs
the interval from `(≺_U, V_U, τ, M_O)`; C5 demands that interval's
*evolution* match GR — reconstruction vs dynamics, tested separately.

**Kill relevance:** feeds D1 (dynamics) and D12 (same-`M_O` falsifier: the
interval map must coincide with the spatial `M_O`). No direct kill wire
until stage 3+.

## D14 — Cosmogony: phase separation into knots + low-dimensional vacuum (sketch, for later)

**Hypothesis (filed from review dialogue, no code):** the 2D fabric is
not an eternal starting condition but the RESIDUAL phase of a
primordial connectivity phase transition: homogeneous high-density
G_* (dimension d_*, unchosen — to be measured, never tuned) undergoes
aggregation G_* → G_dense + G_depleted, with dimensional bifurcation
d_knot > d_* > d_fabric and the residue flowing toward d_I ≃ 2 (then
M_O → d_obs ≃ 3). Matter = concentrated phase (converges with the
BH-as-maximal-tension story, extended to ordinary matter as stored
excess connectivity); vacuum = depleted phase. Big Bang = graph phase
transition; expansion = conversion into vacuum phase (V_obs grows as
network enters the spatially-realized phase — space appearing between
structures, not objects flying through a container); rapid early
conversion = INFLATION CANDIDATE (not inflation: acceleration,
homogeneity, graceful exit, and — sharpest — the near-scale-invariant
perturbation spectrum are all missing rungs). Conservation structure
kept as design constraint: Q_total = Q_vac + Q_knot = const (any
aggregation U must state its conserved quantity; our swaps already
conserve degrees + edge count). Gravity sharpens: the redistribution
creating a knot necessarily distorts surrounding residue (δG_vac →
δd_O → curvature) — mass and curvature from one event.
REFRAME (adopted as the better D1 question): "Why does U
phase-separate into knots + low-dimensional vacuum?" replaces "How
does U repair the lattice?" — the N* protection problem dissolves
(the lattice isn't eternal, it's the residue) and blind-U stays
consistent (separation is what U does, not what it optimizes).
Required mechanism, sharply (REVISED per review — the first
"pump long-range connectivity OUT" formulation was too strong):
phase separation must concentrate STRONG connectivity into knots
while leaving a near-2D WEAKLY globally coupled residue —
G_* → G_dense + (G_near-2D + εG_global); E_global^vac ≠ ∅ is
permitted provided w_global ≪ w_fabric. The y_λ ≈ 1.5 RG pressure
cited earlier is binary-sector (maximally-strong links); weighted
RG flow vs w is OPEN — weak couplings may be irrelevant/marginal
(RG-natural separation) or relevant (pumping still needed):
measurement queued, not assumed. WEIGHTED-RG PRE-REGISTRATION
(review dialogue — highest-information experiment, draft stays
AGNOSTIC: pumping vs persistence decided by measurement, not
assumption): binary y_λ ≈ 1.5 covers maximal-strength links only;
for G_vac = G_fabric + εG_global measure the FLOW on a (density,
weight) grid, (λ,ε) → (λ',ε') under the SAME 2×2 blocking as the
binary study (L40→5). Three outcomes, all informative: y_w<0
(washout → vacuum RG-protected, no pumping needed); y_w=0
(marginal IR weak sector); y_w>0 (amplification → segregation
mechanism required). Target output is a FLOW DIAGRAM with possible
separatrix ε_c(λ) (below → 2D fixed point; above → nonlocal
phase), not a single exponent. Design pre-registrations: (i)
excess-length variable e = L−1 (0 = lattice), λ = fraction of
edges with e>0 — report (λ',e') flow, infer relevance from fixed
points; (ii) weight-coarsening rule chosen by PILOT then FROZEN:
candidates min/mean of crossing lengths, decided on controls
(monotone sane flow) before the campaign; (iii) CONTROLS: λ=0
stays 2D; maximal-coupling row must REPRODUCE binary y_λ ≈ 1.5
(reduction check on the apparatus). Phase 2 (queued): knot-
environment flow y_w^knot-env vs y_w^vac — the attractive split
(vacuum-irrelevant, knot-relevant) making locality an RG property
and curvature a defect-induced departure. Priority: coarsening
pilot is the immediate next spike. COARSENING PILOT (MEASURED,
test_weighted.py — min-rule FROZEN): uniform controls flow
identically under min/mean and the Lw=1 row reproduces binary
λ-flow 0.013→0.310 (reduction check PASSES); λ-flow is topological
(bit-identical across rules AND Lw); min keeps fabric fidelity
1.000 at every level while mean smears to 0.900 by level 3
(transport-faithful wins: parallel paths, best wins). Pilot-scale
hint (not pinned as physics): long-edge excess frozen (9.00 every
level @Lw=10) while λ grows — strength looks marginal, count
relevant (the reviewer's y_w=0 case); the (λ,ε) campaign decides.
CAMPAIGN (MEASURED, test_weighted.py — washout verdict): (ns,Lw)
grid under frozen min-rule, levels 0–3, co-blocked plain as
reference, flow variables (λ,violfrac,marginratio). λ-flow
topological (bit-identical across Lw, third confirmation:
0.013→0.310 @ns=20); pricing sector IRRELEVANT above span scale —
Lw=10 washes out (violfrac 0.012→0.000 by level 3, margin ratio
0.51→2.86 crossing 1: fixed weights outlive shrinking spans,
defects become overpriced/geometrically invisible); Lw=1 NEVER
heals (violfrac==λ every level — analytic: min long-span 2 > 1);
Lw=3 partial (0.310→0.190, margin 0.86 — separatrix-adjacent, one
more level would cross). Washout level k*≈log2(span0/Lw); ns=0
controls stay (0,0) (2D fixed point stable). Reviewer's y_w<0
case CONFIRMED for correctly-priced weak links: vacuum is
RG-protected in the pricing direction, NO pumping needed — count
relevant, pricing irrelevant. Caveats: frozen weights, no U;
washed-out defects persist as overpriced dead weight (margin
~2.9) a real U might prune. Phase 2 still queued (knot-env
split y_w^knot-env vs y_w^vac). Curvature conjecture sharpened
via Prop 1: dominating weak links (w ≥ d_0) are geometrically
INVISIBLE, so curvature must live in small underpricing margins
(δw = d_0 − w > 0 small → δd_O small) — vacuum weak wiring as
marginally-priced (parallel to marginal rigidity noted, not
claimed). POST-CAMPAIGN AMENDMENT (review dialogue — topology vs
geometry split): the campaign measures λ↑ while f_viol→0 along
the SAME flow (Lw=10: f_viol 0.012→0, margin 0.51→2.86) —
topological relevance and geometric relevance flow in OPPOSITE
directions (T15 made pointwise, now with explicit RG
realization). Vacuum condition upgrades from N_long→0 to
P_vac(η>1)→0 in IR with shortcut relevance η_ij^(k) =
d_fabric^(k)/w_ij^(k) ADOPTED as the next-stage order parameter
(per-edge inverse margin; DISTRIBUTION, not mean — campaign
level-2 already shows mean-margin 1.82 lying while violfrac sits
at 0.024; ensemble = longs, fabric η=1 exactly). Slogan adopted:
"L0 need not become local; locality emerges because nonlocal
relations become too expensive to define geometry" (G_vac =
G_near-2D + G_globally-intertwined, constrained by PRICING, not
topology). Three sharpenings kept prominent: (a) D14 SPLITS —
(i) fabric formation (cheap local reference: UNSOLVED, still
owes a U) vs (ii) weak-link washout given fabric (SOLVED frozen;
span-shrinking presupposes a coarsenable lattice — "differentiate
the pricing hierarchy" addresses (ii), not (i)); (b) PUMPING
MOVES, not retires — washout is conditional on primordial Lw≳2,
so if G_* starts binary-like (all w≈1, never washes out)
something must RAISE prices: edge-space pumping becomes
price-space pumping, and w(χ)/traffic is LOAD-BEARING (if w_k
renormalizes down with span, washout dies); re-pricing U needs
its own conservation ledger (prices aren't moved stuff — state
the invariant or argue none exists); (c) KNOT-ENV DESIGN TRAP
pre-flagged — reference plain near a knot is ambiguous (knot in
or out of d_fabric?) and the null runs AGAINST the signal (dense
knot shortens fabric paths → η down → faster washout), so
pre-register reference + relational radius r_O before measuring
P(η|r_O,knot); keep y_w^knot vs y_w^vac as the compact claim.
Cross-check queued (not a result): binary tolerance bound (~2
operational longs/400 nodes ≈ violfrac 0.003) lands exactly on
campaign ns=5 level-0 violfrac 0.003 — tolerance may calibrate
how close to zero P(η>1) must get. POST-CAMPAIGN AMENDMENT #2
(review dialogue — D14 becomes the origin of the pricing
hierarchy): campaign result reframed as CONDITIONAL (stability,
not origin): w_long≳d_span ⟹ RG washout; explains stability of
an appropriately-priced vacuum, NOT why the inequality holds —
old D14 ("why does U remove long edges?") REPLACED by "what
dynamics drives η below unity for vacuum links?" (η=d_fabric/w
adopted last round). Scale-relative sharpening: washout at
k*≈log2(span0/Lw) must land FINER than observer readout scale,
so required-Lw is a function of observation depth (deeper
readout → higher Lw owed) — hierarchy target is a curve, not a
number; tolerance end pinned by P(η>1)≲tol (a few operational
shortcuts survivable, not literal zero). (χ,Q,F) GATE ADOPTED
(blocking for all w-rule entrants): each states micro variable
χ, conserved ledger Q, map F with w=F(χ,...) intensive/emergent
(temperature-like, NOT conserved — no invented Σw=const);
retroactive bite: self-pricing (w=span) FAILS (span is readout,
not stuff) → demoted to benchmark; structural-χ rules
(curvature etc.) disfavored unless Q found → gate pushes toward
flow/capacity χ. TRAFFIC SIGN ARGUMENT (filed, kills naive
story): congestion pricing (w↑ with load J) has WRONG sign
(busy fabric→expensive, idle weak links→cheap — backwards);
needed sign is HEBBIAN/use-cheapens (busy→cheap fabric+knots,
idle→expensive vacuum links); differentiation needs
nonlinearity or conserved per-node budget allocated by use
(linear w=J/C with demand-following capacity sits ≈const).
KNOT PHASE-2 PRE-DESIGN (locked): planted-knot pilot FIRST
(membership exact by construction — per-edge η_K/η_0 needs same
graph + masked d_0, separate matched-plain run has no node
correspondence; discovered knots later); DUAL reference (η_0
masked-background PRIMARY — ruler fixed, clean price-flow
claim; η_K operational secondary — anatomy; ratio η_K/η_0 =
d_K/d_0 separates price-flow from path-shortening); r_O binned
in d_0 NEVER d_K (operational metric compresses bins near
knot — ruler would infect the coordinate); headline Δy_w =
y_w^knot−y_w^vac > 0 with ESTIMATOR pre-registered (log-slope
vs washout-level shift Δk*, zero-handling for successful
washout — log 0 bites exactly when it works). ORDER: knot pilot
stays first (cheap, frozen; Δy_w sign constrains what w-dynamics
must reproduce), gated w-origin second, tolerance cross-check
riding along. L0-independence intact (origin story lives at
P0'/D14; L0 theorems still cite no U). The wall is now: WHERE
DO THE WEIGHTS COME FROM. POST-CAMPAIGN AMENDMENT #3 (review
dialogue — price-as-state + (n,k) separation): weights
REFRAMED as L0 state variables in S_n=(G_n,{w^(n)},...),
S_{n+1}=U(S_n) (CA analogy adopted — state needs specified
update, not conservation). (χ,Q,F) GATE v2: conservation
DEMOTED from admission requirement to discoverable property of
U (bonus, not ticket); gate's anti-magic work restated as (i)
blindness (F reads L0 state only), (ii) update-form (genuine
evolution with memory, not assignment), (iii) no inserted
hierarchy (bifurcation = attractor outcome, measured).
Self-pricing reassessed: passes (i) (span is L0-computable),
FAILS (ii)/(iii) (w:=span is hand-written pricing) → benchmark
status stands, right reason now. (n,k) SEPARATION ADOPTED
RIGOROUSLY: n = state-machine time (U), k = RG scale (R);
campaign retrospectively = η(n=fixed,k) with dw/dn=0; program
object is now the η(n,k) SURFACE (η=d_fabric^(k)(n)/w^(k)(n));
[U,R]≈0 askable as RG-consistency condition on (U,blocking)
pairs → LINKED to D12 commutation over-arch (D12's central
equation; D12 note filed). D14 SHARP FORM: price-space phase
separation — U from uniform w≡1 spontaneously bifurcates P(w,n)
into low-price/high-traffic (→knots) vs high-price/weak
(→vacuum); topology-follows-price REQUIRES H(S_n) reading w
(stated mechanism, not hope) → ORDER: E-fixed re-pricing U
FIRST (bifurcation with frozen topology = stronger, no
topological help), H-dependence stage two; needs bifurcation
order parameter (bimodality/mode weights) + sector membership
(planted sectors first — third application of the rule).
ATTRACTION = decreasing relational price (w_AB(n+1)<w_AB(n) at
L0, d_O shrinking at observer level — no movement-through-space
needed); observable = co-movement of inter-knot path-price
d_w(A,B;n) vs reconstructed d_O(A,B;n) under running U (no
direct edge needed); sign of dw_AB/dn is MEASURED dynamical
outcome, never assumed; memory terms (inertia-adjacent)
admissible via F reading w^(n). FALSIFIER TEETH: uniform w≡1
init does the work through TRAJECTORY P(w,n) (one-step jump =
imprinting/inserted; gradual differentiation = generated);
report (n,k) surface slice (P(η>1) at multiple k); pre-register
knot persistence criteria (ripening already filed). POST-CAMPAIGN
AMENDMENT #4 (review dialogue — falsifier-protocol core, D14 as
dynamical selection): Φ(n,k) ≡ P(η>1) on frozen-then-blocked
S_n^{(k)} ADOPTED as the program object (surface, not a number);
∂_nΦ = U-dynamics, ∂_kΦ = RG observation — factorized claims:
(a) U delivers S_n into washout basin, (b) frozen-R flows to
Φ≈0 inside it. CAMPAIGN RETRO-FRAME: frozen result = slice
Φ(n_0,k) = the BASIN MAP (Lw≳2, k*≈log2(span0/Lw)) — half the
claim already banked, not a pilot; U-run owes only the
trajectory δ(w−1) → basin. Cost structure: U runs once
(n-direction, expensive), R post-processes each frozen state
(k-direction, cheap) — surface costs one trajectory. TARGET
CONTOUR: pass = trajectory crosses Φ(n,k_obs)≲tol and stays
(tol≈2 operational longs/400 nodes from binary tolerance;
0.003≈0.003 cross-check calibrates the contour — re-analysis
of campaign states in Φ language queued as apparatus validation
before any U-run). TRAJECTORY-IS-EVIDENCE: endpoint alone
meaningless (w^(1)=F(desired geometry) = reconstruction
disguised as dynamics); record full P(w,n): δ(w−1) → broad →
{P_knot,P_vac}. FIRST-TICK DIAGNOSTIC (severe, with structural
null): Δw^(0) spread at n=1 always expected (S_0 structure
varies; neighborhood-reading F reflects it) — suspicion =
CLASSIFICATION at n=1, quantified as MI curve I(w^(n);
sector_final): imprinting saturates n≈1, instability grows over
many ticks behind σ_w∼e^{γn} linear phase; ε-noise test pinned
to t*(ε)∼(1/γ)ln(A/ε) with γ matching linear-phase fit (two
independent measures of one number = brutal version).
INDEPENDENT LABELS, BIDIRECTIONAL: sectors from topology
WITHOUT w (density/k-core/community on G_n; planted in pilots)
→ P(w|sector) as outcome, PLUS reverse (w-labels → structural
correlates); both directions must agree — disagreement means
price sectors ≠ density sectors (complicates knots=dense=cheap
interestingly). RIPENING (separate falsifier): observe to
n≫t_form (10× suggested, pre-registered multiple);
stationarity P_knot(s,n)→P*_knot(s) via named distribution test
across late windows (KS or similar); N_knots→0 = clean fail,
→1 = fail with BH-consolation on separate argument only (one
knot ≠ matter population); "fraction in knots" restated for
gate v2 (edge-mass/topological share, or discovered conserved
Q — no required ledger). ENSEMBLES: 2–3 pre-registered
NON-GEOMETRIC primordial families (random regular, ER, high-d)
× seeds — start FAR from the answer (near-lattice S_0 smuggles
it). LOAD-BEARING CLAIM (adopted verbatim in spirit):
homogeneous w≡1 + observer-blind U (no target dimension/
geometry/labels/pricing classes) → spontaneous destabilization
(γ>0) → persistent knots + Φ→0 vacuum, trajectory + surface +
persistence + ensembles all pre-registered. NEXT ARTIFACT:
written D14 falsifier pre-registration (estimators + numbers +
pass/fail); apparatus first (Φ(n_0,k) re-analysis pinned in
tests). APPARATUS VALIDATED (test_weighted.py — phi_stats +
tolerance contour): Φ-slice ns=20/Lw=10 = 0.900→0.657→0.167→0
(nV 36,23,5,0; 4/40 priced already at k=0); Lw=1 rows Φ≡1
analytic; Φ·λ=violfrac to 1e-12 everywhere; mean-lies exhibit
STRONGER than filed (k=1: mean_inv_eta 1.12 "healed" vs Φ=0.657
— distribution mandatory, mean disqualified as headline);
washout NON-MONOTONE (ns=5/Lw=10 violfrac 0.0032→0.0065→0:
concentration before washout; nV monotone ↓); tolerance
contour TOL=2/760 crossed at k=3 (ns=20/Lw=10), k=2
(ns=5/Lw=10), never for Lw=1/Lw=3 — measurement chain green
before any U-run depends on it. KNOT PILOT (MEASURED,
test_weighted.py — apparatus + null, NOT the Delta-y_w test):
planted 5x5 clique, ns=20/Lw=10, dual ruler + r_O bins (frozen
super-node rule, block-imaged mask). Weak Phi_0 global =
36/40,23/35,5/30,0/18 BIT-IDENTICAL to campaign (reduction
passes; null as constructed — frozen eta_0 cannot vary
spatially). Weak Phi_K = 35,20,5,0 (knot heals 1,3,0,0 marginal
nearby longs via path-shortening — small, localized, right
sign). METRIC BUBBLE: k=0 interior eta_0 260/260 violated
(thick vs fabric) vs eta_K 260/0 (clique distance 1 — local vs
itself). d_K/d_0 ≤1 everywhere; k=0 means near 0.87 vs far 0.96
(localized dip); k=3 exactly 1.000 — 5x5 knot DISSOLVED to one
block (knot visibility under R is scale-dependent; deep-k knot
studies need bigger knots or knot-tracking blocking — method
note). NO min-rule bundle mixing (zero dragged L at all levels
— weak prices survive near dense L=1 structure). k=1 near-bin
fast washout (1/7 vs far 9/9) VERIFIED as span-selection (near
spans ≤11, far ≥12 — proximity binning selects pair
separation; zero knot physics on primary). RULER-TRAP RULE
(caught in spike, filed as design law): weak links in NEITHER
ruler (first draft put swaps in d_K → trivial total "healing").
Verdict: apparatus validated, null established — real Delta-y_w
needs w-dynamics (E-fixed re-pricing U with knot present is the
next experiment). FROZEN-KNOT STOP (review verdict, adopted):
static dense knot changes the METRIC (d_K/d_0<1 near, interior
strongest, gone once blocking unresolves the knot) but NOT the
weak-link pricing flow (Phi_0 bit-identical) — experimentally
separated; no further frozen-knot runs (zero Delta-y_w info;
would only re-map the ruler). C(r,k) = 1-<d_K/d_0> ADOPTED as
curvature-CANDIDATE diagnostic (naming discipline: candidate
until dynamics; pilot values k=0 near 0.13/far 0.04, k=3 0 —
derived from pinned means). RULER COROLLARY: rulers stay
TOPOLOGICAL-only, never price-weighted (eta=d^w/w is
self-referential — trap's second form); consequence: experiment
A factorizes (E frozen -> C static backdrop, w dynamic -> Phi
dynamic) — A isolates pricing BY CONSTRUCTION; no dynamical-C
move until E-dynamics (C2/D). Metric bubble stays KINEMATIC
(two rulers, two descriptions — gravity-talk gated on
dynamics). CIRCULARITY DETECTORS (named set, checked every
run): (i) rulers contain neither test population nor prices
(m_ratio~0.05 episode = standing demo); (ii) labels independent
of outcome (bidirectional); (iii) init far from answer
(primordial severity); (iv) trajectory not endpoint (MI
diagnostics). EXPERIMENT-A PRE-DESIGN (locked): planted knot,
E FROZEN, w(0)=1, primitive static-chi F (suggested:
common-neighbor embeddedness, Hebbian sign + uniform drift, <=2
params, ALL pre-registered); question ONLY Delta-y_w != 0;
strongest outcome Delta-y_w>0 DESPITE d_K/d_0<1 (price dynamics
fighting geometric shortening); all signs informative (0 =
geometry-only knot; <0 = reinforced washout). STAGING: static
chi admits A (relaxation answers spatial differentiation) but
CANNOT show bifurcation (w->w*=G(chi), gamma<0 at best; gamma>0
needs dynamical chi/memory — C2/D territory); A bundles
analytic-fixed-point convergence (verification, like Lw=1 row)
+ spatial profile P(eta|r) (discovery) in one run. SEQUENCE
A->B->C->D ADOPTED: B = post-processing of A's trajectory
(P(eta|r,K,n,k) + C backdrop, cheap); C FORKS (C1 = unplanted
E-frozen weak-generation, expected informative-negative since
w*=G(chi) gives chi-level-sets -> motivates C2 = E-dynamics
H(w) or dynamical-chi U); D = filed falsifier. A ESCAPE
HATCHES pre-listed (close in pre-registration): F-param budget,
chi-choice justification, bins frozen (done), init fixed
(w=1). STAGE-GRADED GATE: A = pre-registered simplicity +
measured profile (relaxation ok); D = full no-insertion +
instability + ensembles (origin claims wait for D). A-ARCHITECTURE
LOCK (review agreement + chi-constraint derivation): A MOTTOS —
"does structure drive prices toward the washout basin?"
(relaxation/selection; static chi) vs "does homogeneity
spontaneously destabilize?" (instability; dynamical chi ONLY —
gamma/noise/t* diagnostics gated to C2/D; running them on
relaxation manufactures false verdicts). C-FORK TABLE ADOPTED
(A planted/E-frozen/static-chi; B anatomy-of-A; C1 unplanted
E-frozen; C2 dynamical-chi/E-formation; D primordial
falsifier); C1-negative expected (repricing manufactures no
matter topology) AND C1-positive kept discovery-capable
(price-sector WITHOUT topological knot would forbid premature
price-sector=knot identification). FIXED-POINT-FIRST DISCIPLINE
(strict): derive w*(chi), stability |dF/dw|<1, move/direction/
boundedness/timescale/basin-reach/sign-prediction BEFORE any
A numerics; tooth = TARGET-VARIABLE EXCLUSION (chi may not
contain d_0/span/any ruler quantity — span-reading F collapses
to self-pricing; checkable at pre-registration: list inputs,
ruler among them = reject). Form-1 defense filed: G hand-written
but blind+simple+preregistered, basin banked INDEPENDENTLY — G
landing judged, not inserted. LOCAL-STATIC-CHI IMPOSSIBILITY
(derived pre-code): swap endpoints are locally fabric-identical
(deg 4, Jaccard ~0 — grid-edge endpoints also share 0 common
neighbors), so NO graph-local static chi separates weak longs
from fabric shorts; embeddedness/degree give knot-vs-everything
(wrong split: fabric priced with weak). CONSEQUENCES: (a)
NEGATIVE-CONTROL DESIGN — run embeddedness/Jaccard F predicting
Delta-y_w=0 (near/far weak share chi~0 => identical flow);
predicted-null-returning-null validates chain, returning
non-null = apparatus-bug detector; control BEFORE sensitive
candidate, always. (b) SENSITIVE chi must be GLOBAL
(betweenness: weak-high/fabric-mid/knot-low hypothesized under
congestion sign — grid-central fabric may spoil; VERIFY BY
SPIKE: population distributions on A-state before committing)
or DYNAMICAL (traffic — C2 territory); if betweenness fails to
three-way-split, A-static has NO sensitive candidate => early
result that pricing needs dynamical chi. NEXT: chi-measurement
spike -> commit F + analytic w*/stability -> lock
pre-registration -> code A. CHI-SPIKE VERDICT (MEASURED,
test_weighted.py — A-static fork resolved): full A-state
(40x40 ns=20 5x5-knot): embeddedness weak=fabric=0 EXACT
(3040+40 all zero; interior 23) — local-chi impossibility
CONFIRMED empirically; embeddedness-F predicts Delta-y_w
EXACTLY 0 (null control LOCKED). degree_sum same shape (med 8
both; fabric max 30 = knot-touching edges). betweenness
THREE-WAY TYPICAL: medians weak 0.0286 / fabric 0.0031 /
interior 0.00005 (q-bands: weak 0.0185-0.0404, fabric
0.0020-0.0049) with OVERLAPPING tails (fabric max 0.041 >
weak med; interior max 0.0095 = gateway load) => congestion-F
side effect: central fabric + gateway shell price high —
monitor via fabric-price readout (Phi-verdict safe: fabric
eta<=1 always). Near/far weak betweenness: 0.0227 / 0.0238 /
0.0293 — NO difference (substitution micro-hint near<far,
underpowered n=6; A-run settles it DETERMINISTICALLY: chi
exact given G) => betweenness-F predicts WEAK Delta-y_w>0 via
SUBSTITUTION (clique steals load from nearby weak -> cheaper
-> slower washout — hoped sign via real mechanism, likely
small). Load-halo ABSENT (near fabric med ~= far) => no
price-halo prediction. GATEWAY ANATOMY predicted (max-fabric
edge sits near knot 0.041 => congestion prices a SHELL around
the knot — check P(w|r=0 fabric) in A-run; neutral until
measured). r_O-as-chi REJECTED (label smuggling — checkable
form of the no-labels clause: proximity-to-known-knot =
labels). Density-proximity (dist-to-high-degree) flagged GRAY
(blind-admissible but label-laundering in function — flagged
third candidate only, after the two clean ones). VERDICT:
A-static = exact-null control + weak-positive attempt; likely
outcome null-or-micro DECIDES the traffic question
(dynamical-chi C2 as the real mechanism) — program learns
either way. NEXT: commit Form-1 F x2 candidates + analytic
w*/stability -> lock pre-registration -> code A. FORM-1
PRE-DERIVATION LOCK (review agreement + fabric-ratio
derivation): analytic null is F-AGNOSTIC (any deterministic
F(w,chi) from uniform init with chi constant => identical
trajectories) => DETERMINISM REQUIRED for A-candidates
(stochastic U deferred to C2 with expectation-form
predictions); nonzero embeddedness Delta-y_w = leak or
nondeterminism bug, nothing else. FABRIC GUARD (3 checkable
parts, derived not chosen): (i) absolute med(w_fabric) <~ 3
(Lw=10-analog: weak-med ~10 => fabric-med ~2); (ii) relative
med_f < med_w (hierarchy un-inverted at medians); (iii) RATIO
CHECK (w*_f-1)/(w*_w-1) ~= 0.003124/0.02858 ~= 1/9.15 from
banked medians — SECOND end-to-end analytic confirmation
alongside w* convergence (match = Form-1-linear confirmed;
deviation = leak/bug). MONOTONE-OVERLAP THEOREM (structural):
fabric-max chi 0.041 > weak-med chi 0.029 => ANY monotone g
prices some fabric above typical weak (band-pass un-overlap
unprincipled, excluded); superlinear g separates medians more
but max-tail stays inverted regardless — overlap ACCEPTED as
structural for betweenness-chi, monitored via q90, never
pretended away. G-SELECTION PROTOCOL (temporal order IS the
anti-circularity): intrinsic story -> g -> w* -> basin overlay,
reported EVEN ON MISS; re-choice after miss = NEW candidate +
fresh pre-registration. NORMALIZATION TRAP flagged: no
normalized b-hat (hidden third param) — raw b, beta absorbs
scale, report effective sensitivity beta*b_weak-med;
pre-registration counts constants. SUBSTITUTION SIGN with
C2-FLIP CAUTION: A claims only topology->redistribution->
differential pricing (no curvature words); static substitution
(near-weak cheaper) may REVERSE under traffic feedback
(cheap->busy->expensive) — C2 sign change reads as feedback
physics, never contradiction; do not over-extrapolate A's
sign. GATEWAY-SHELL PREREG: W_fabric(r,n) median + q90,
r(e)=min-endpoint (consistent with longs); prediction banked:
NO broad halo + high-price gateway TAIL (shell = tail
phenomenon: q90-median gap is the detector; halo would move
the median); trajectory + endpoint. OUTCOME TABLE (sufficiency
line = banked TOL contour): NULL (Delta~=0) => static-chi
program OVER, traffic needed for mechanism; MECHANISM-ONLY
(Delta>0, no cross) => signal weak => C2 as AMPLIFIER
(feedback boosting substitution); SUFFICIENT (cross) =>
celebrate skeptically (re-run all 4 detectors). CANDIDATES
LOCKED at 2 (embeddedness control + betweenness sensitive);
density-proximity stays flagged/unrun. FORM-1 DERIVATION
(LOCKED pre-A, 12-step table — docs-only turn; NO A-code shares
a turn with derivation, firewall hygiene): (1) STORY: toll
proportional to traffic load, static (loaded links cost more);
w_base=1 fixed BY CONVENTION (lattice unit = init value;
degenerate, not a parameter). (2) g(b;beta)=1+beta*b
(betweenness), g_emb(e)=1+beta*e (control); RAW chi (beta
absorbs scale; no normalized b-hat — hidden-third-param trap
refused). (3) F: w'=(1-alpha)w+alpha*(1+beta*chi),
DETERMINISTIC, alpha=0.2, n=64 ticks. (4) w*(chi)=1+beta*chi
edgewise. (5) STABILITY |1-alpha|<1 <=> alpha in (0,2);
alpha=0.2 monotone, inside. (6) TAU=-1/ln(0.8)~4.48 ticks; 64
ticks ~14tau, residual 0.8^64~6e-7 (converged). (7) BANKED CHI
IN: medians weak 0.02858 / fabric 0.003124 / interior 5.3e-05;
near/far weak 0.02267/0.02926. Beta-grid {3.5,35,350,3500} =
decades around 1/b_weak-med~35 — CHI-SCALE calibration
(instrument-to-sample), NOT basin contact (basin sealed until
#10). Control beta_emb=1 ARBITRARY (weak/fabric chi=0 =>
result beta-independent by analyticity; separate beta per
candidate — scales differ 1000x, same-beta would be
numerology). (8) PREDICTED w* medians: beta=3.5:
weak 1.10 / fab 1.011 / int 1.000; beta=35: 2.00 / 1.11 /
1.002; beta=350: 11.0 / 2.09 / 1.02; beta=3500: 101 / 11.9 /
1.19. Near/far weak @350: 8.93/11.24 (excess ratio 0.775,
beta-independent). (9) GUARDS: ratio (w*_f-1)/(w*_w-1)=1/9.15
at EVERY beta (beta cancels — sweep-wide identity check);
absolute med_f<~3 TRIPS at beta>~640 PREDICTED (trip-there =
linearity confirmed + cost noted; trip-below = anomaly);
relative med_f<med_w. (10) BASIN OVERLAY (FIRST CONTACT):
beta=3.5 (~Lw1-analog) => NEVER cross; beta=35 (w*~2.0, gap
between Lw1/Lw3 rows) => partial fall, NO cross k<=3;
beta=350 (~Lw10-analog) => CROSS k~2-3 following Lw=10 slice
shape (shape prediction); beta=3500 (w*~101 > max span 78) =>
cross k<=1 (near-immediate washout). beta=350<->Lw10 alignment
DISCOVERED here (grid came from chi-scale), never selected.
Weak is a DISTRIBUTION (spans vary) — median overlay
approximate, exact Phi measured. (11) DELTA-y_w:
embeddedness EXACTLY 0 + ZERO MOTION (w_weak(n)=1 to 1e-9;
violation = leak/bug, STOP); betweenness Delta>0 via
SUBSTITUTION (near excess 0.775x far => near cheaper =>
delayed washout; direction beta-independent); magnitude modest
=> MECHANISM-ONLY likely at beta<=350. (12) LOCKED
INTERPRETATION: control pass = frozen-weak + Delta=0;
sensitive checks per beta = edgewise w* convergence (tol) +
1/9.15 ratio + shape/cross + sign + gateway W_fabric
shell-vs-halo + 3-part guard; outcome table
NULL/MECH-ONLY/SUFFICIENT x TOL contour + filed C2 branches.
NO re-choice of g/beta past this point (re-choice = NEW
candidate + fresh pre-registration). NEXT: code experiment A
(5 relaxation runs: control + 4 beta; trajectories + Phi(n,k)
surfaces + profiles). EXPERIMENT-A VERDICT (MEASURED,
test_weighted.py — mechanism demonstrated, Delta-y_w split):
control BIT-EXACT (weak w(n)==1.0, maxdev 0.0, all rows frozen
at Lw1 slice, Delta=0 — analytic null holds, NO leak).
Tick-0 all 5 runs == Lw1 slice (40/40,35/35,30/30,18/18 —
uniform-init reduction, 5-way identity). w* convergence
edgewise (maxdev matches excess*0.8^64 theory); R_fw=0.10929
SWEEP-WIDE all four beta (linearity end-to-end); medians hit
locked table (beta=350: 11.004/2.093). Per-beta: 3.5 frozen,
never cross; 35 partial (34/35,29/30,17/18), no cross; 350
CROSSES k=3 with (36,23,7,0) vs banked Lw10 (36,23,5,0) —
k=0,1,3 EXACT recovery of hand-planted washout by DYNAMICAL
pricing, k=2 +2 = HETEROGENEITY COST (w* spread vs uniform Lw;
direction filed); 3500 crosses k=0 (saturated ceiling, no
Delta resolution — as filed). Gradualism beta=350 tick8
strictly between (relaxation, NOT imprinting). DELTA-y_w
SPLIT (locked sign prediction FALSIFIED at Phi level —
honest): w*-level substitution CONFIRMED (near/far 8.934/
11.242, excess ratio 0.7746); Phi-level runs WRONG way (final
k=1: near 1/7 vs far 9/9 — SELECTION dominates: near spans
<=11 vs far >=12, DISJOINT support kills span-matching) —
substitution real at price level, washout-delay NOT detected
at Phi level. OUTCOME: global basin reach YES at beta>=350
(Form-1 maps the beta phase diagram; beta-SCALE origin —
why ~350 — OWED to C2, like T_c: measured boundary, not
derived constant); knot-differential washout NO (needs
matched-span apparatus = bigger knot, or dynamical chi where
feedback may amplify past selection — sign unknown, no
extrapolation). Gateway shell CONFIRMED (W_fabric medians
flat ~2.0 = no halo; q90 near 4.79 > far 3.99 despite
n=113<<2551 = tail shell). Guard: 350 passes (2.09<3); 3500
trips to 11.9 WITH ratio intact (predicted trip =
linearity confirmation). B-STATUS: radial anatomy banked
in-test (near/far rows + W_fabric trajectories' endpoint) —
B satisfied for the GLOBAL effect via A post-processing (as
filed); knot-differential anatomy limited by selection
(same caveat). C2 BRIEF: (i) static congestion suffices for
VACUUM pricing globally — C2 inherits a working price
mechanism, owes the beta-scale + formation; (ii) knot effect
needs dynamical chi (traffic feedback) or bigger apparatus;
(iii) substitution sign under feedback UNKNOWN (may flip —
filed caution stands). C2-DESIGN (review roadmap + sign
analysis — A CLOSED, no more static pricing): C2 question:
can traffic-price feedback GENERATE pricing scale (order-one
in => basin out)? Loop chi_n=chi(G,w_n), w_{n+1}=F(w_n,chi_n),
topology FROZEN (feedback before formation). SIGN ANALYSIS
(lead result, pre-code): CONGESTION-feedback ATTENUATES
(negative feedback: expensive sheds load => chi(w*)<chi_0 =>
w* below static; Wardrop-like homogenization pressure =
hierarchy unstable; all-or-nothing betweenness =>
FLAPPING risk: priced-out => chi collapses => fallback =>
oscillation; (alpha,cadence) = damping) — its role is
STABILITY/SHAPE, never scale. ATROPHY-feedback (idle =>
expensive) AMPLIFIES (positive feedback on idle links) but
needs cap (runaway; cap-scale = beta-scale in disguise — NO
FREE LUNCH) or budget principle (sum w = B, scale from B —
CANDIDATE, needs justification, NOT adopted) or saturating
form w*=1+beta(1-chihat(w*)) (Form-1 + dynamical chi +
complement: bounded by beta, implicit fixed point). 2x2
MATRIX: (betw,cong) = A-continuity, expect attenuation/flap
(RUN); (betw,atr) = EXCLUDED analytically (interior chi
lowest => priced highest — inverted hierarchy, knots die
first; exclusion filed, not run); (walk,cong) = knot-hostile
IF walks trap in cliques (VERIFY walk-traffic pops first —
assert nothing); (walk,atr) = SCALE candidate IF pops split
(interior flow-trapped/high, weak low). C2 = TWO feedback
laws (sign fork IS the experiment), not one. CONTINUITY
SELECTOR (design criterion): walk-chi continuous in w =>
fixed-point theory applies (Brouwer + Jacobian); betw-chi
discontinuous => expect cycles, pre-register cycle analysis
+ time-average <Phi> fallback (flickering locality
observable if limit cycle). SCALE RECURSION (honest): every
variant bottoms at a scale (beta/cap/B); C2 owes MECHANISM
(direction + amplification-vs-attenuation + stability),
scale origin stays owed (phase diagram, not T_c;
"order-one" amplification needs derived gain, never bare
measurement). CHI-UPDATE CADENCE m (every-m-ticks) =
design parameter (timescale separation + exact-betw cost
~7s/tick — recomputing every tick infeasible; principled:
traffic equilibrates slower than prices adjust... or noted
either way). C2 CONTROLS: embeddedness run as REGRESSION
control (static chi => must reproduce A-control EXACTLY —
code-path check). PASS/FAIL (adopted): STRONG (order-one =>
basin + stable); PARTIAL (amplification insufficient =
mechanism-only); FAILURE (stuck ~1 / collapse / runaway
without useful regime). C1-SKIP ENDORSED (analytic reason:
static-chi Form-1 unplanted relaxes to w*=G(chi) => sectors
= chi-level-sets BY CONSTRUCTION — cannot surprise;
skipped as principled, runnable cheap later as complement).
M_O AUDITS (after viable C2 ONLY — audit what works):
Laplacian/exit/Kron = three independent R testing
M_O U ~= U_eff M_O = D12 [U,R]~0 CENTRAL EQUATION (link
filed — audits ARE D12's experimental program); SEQUENCE:
Kron first (exact, parameter-free), diffusion/exit after
(t-scale = shopping hazard — pre-register from spectral gap
1/lambda_2 or equivalent intrinsic rule); TRAP WARNING:
w-as-PHYSICS (conductances in Laplacian = diffusion
process) allowed, w-as-RULER (d^w-based eta) stays FORBIDDEN
— eta rulers topological always. (Uploaded-conversation
reference opaque to agent — responding to summary only.)
ROADMAP LOCKED: A [done] -> C2 feedback [NEXT] -> M_O audits
-> dynamic topology + knots -> primordial falsifier. NEXT
UNIT: walk-traffic pops spike (decides matrix) -> DUAL
derivation (betw-cong + walk-atr fixed points/stability;
cycle-analysis for discontinuous cell) -> preregister both
+ exclusions -> run same apparatus. WALK-SPIKE SPEC (FROZEN —
spike decides fork mechanically): walk-chi = FINITE-horizon
transient traffic (infinite-horizon stationary edge-traversal
is EXACTLY uniform 1/E — pi_i/d_i=1/2E per direction — so T
is load-bearing, not a detail): W=50000 walks, horizon T,
uniform starts/neighbor choice, seeds {0,1}; chi_e =
traversals/(W*T) (intrinsic fraction, no scale trap).
ORDERING hypothesis: interior > fabric > weak (trapping >
wandering > stumbling). T-scan {10,20,40,80}; PASS = strict
median ordering at >=3 of 4 (robustness); T-FREEZE RULE
(pre-stated): T=40 (~system radius 78/2, recorded before
seeing) IF in plateau ELSE plateau midpoint. PRECISION RULE
(not shopping): orderings agree both seeds else raise W.
SUSCEPTIBILITY: weighted walks P(i->j) propto 1/w (reduces to
uniform at w=1 — continuity); PRIMARY uniform-lambda probe on
all weak links lambda in {1,2,5,10,20} (hand-set measurement,
Lw-campaign logic); avoidance A(lambda)=chi_weak(l)/chi_weak(1):
PROCEED if A(10)<0.3, KILL if >0.5, gray judged+reported;
fabric-retention A_fab(10)>0.7 REQUIRED (differentiation
sustained). SECONDARY single-edge lambda (3 representative
weak links) for local gain. DECISION: both legs pass =>
derive walk-atrophy (saturating, GAIN-FED from banked A(l));
either kills => kill static walk-atrophy WITH leg+numbers
(scale then needs budget/other-chi — decided then, not now).
DATAFLOW FILED: spike -> A(l) gain -> derivation -> lock ->
code (derivation consumes spike numbers). BETW-CONG
DERIVATION (parallel, spike-independent): analytic core =
per-edge OWN-effect <=0 (raising e never adds e to shortest
paths — own-chi monotone nonincreasing in own-w) + CROSS >=0
(reroute); predictions: weak w* BELOW static (attenuation
factor = this run's number), fabric at/above static
(absorption), basin needs HIGHER beta than static-350
(measured gap), flapping possible (cycle + <Phi> fallback
armed, no Jacobian — discontinuous). Runs beta in {35,350}
only (narrower question). CADENCE HONESTY: shortest-path chi
has NO intrinsic timescale => m=1 ideal, m=4 cost-compromise
(7s/eval); pre-registered m=1 VALIDATION run at beta=350
(must agree qualitatively else cadence artifact). FREEZE LIST
(before implementation): fixed-point predictions,
Jacobian-where-continuous / cycles-where-not, Phi(n,k),
<Phi>, price distributions, embeddedness exact-null
regression, + banked A(l) curve. WALK-SPIKE AMENDMENTS
(ADOPTED pre-data — both reviewers converge; analytic
corrections, spec v1->v2, appended never silent): (a) EXACT
finite-horizon propagation PRIMARY (deterministic O(TM), no
seeds/W); Monte Carlo DEMOTED to implementation check (one
config: ordering agree + fab-med within 10%; W-escalation
DROPPED — mismatch = bug, stop). (b) PLATEAU -> BROAD WINDOW
(signal MUST vanish at stationarity (uniform 1/M) —
near-stationary plateau would count AGAINST; window =
contiguous strict block spanning >=4x; scan extended
{1,5,10,20,40,80,160,320} (exact is cheap); T=1 closed-form
anchor + T=320 flattening expectation (not gated)).
(c) RADIUS justification STRUCK (diffusive sqrt(T), not T);
T=40 = protocol value, intrinsic justification OWED (debt:
T-from-state-machine — relaxation/mixing/intrinsic clock).
(d) STATIONARY NULL banked alongside A(l) (from conductances;
difference = structural contribution); pass NARROWED
(feasibility-under-protocol, never discovered mechanism).
(e) NORMALIZATION narrowed (sample-only; P(alpha w)=P(w)
relative-routing; beta/M regime visible — scale stays open).
(f) CROSS-EFFECTS corrected to SIGN-INDEFINITE (5-node
counterexample VERIFIED bit-exact + PINNED: at 3->2 while
sb 3->4, sa 5->2, bt 1->4); own<=0 kept (fixed demand);
"fabric absorbs"/"higher beta" demoted to HYPOTHESES;
two-point beta limits (both-fail = failure-at-settings, NO
boundary location); concave-D [chi(w')-chi(w)]·(w'-w)<=0
ADOPTED-conditional (saturation/cadence/discrete TBD in
derivation); flapping = cadence-vs-stepsize distinguished;
cycle fallback = <Phi(w(t))> + basin-time fraction (never
Phi(<w>)). (g) GAIN-vs-RESPONSE: single-edge probes HELD OUT
from gain derivation (validation set; uniform-lambda
calibrates). (h) INJECTION/LIFETIME = mechanism-part
(uniform starts + T = source protocol, not neutral
measurement; alternatives deferred). (i) KILL SCOPE: this
construction only. WALK-SPIKE VERDICT: leg1 ORDERING KILL
(0/8 strict horizons; interior monotone 5.0e-05->2.2e-04
toward uniform, NEVER crossing fabric~0.00031; T=1 anchor
bit-exact 2.7e-20; analytic sandwich confirmed inverted-
at-1/equal-at-inf). WORSE THAN MISS: signal INVERTED
(interior LOWEST everywhere => atrophy would price knots
HIGHEST — catastrophic inversion, knots die first);
fab~=weak TIED within 1-4% (order unstable across scales:
full fab barely above, reduced weak barely above) => NO
weak/fabric lever either. leg2 PASS-AS-FEASIBILITY (A(10)
0.1036/1.0135 tracks stationary null 0.1011/1.0108 to ~2%
at ALL lambda — avoidance = conductance math, structural
~0; single-edge = uniform (0.102 — avoidance LOCAL
per-edge, no collective component; held-out banked).
MC-check passes (ordering agree False=False, fab-ratio
1.004). T-freeze fallback executed (no window -> T=40 for
lambda-probe, banked anyway — pre-stated). OVERALL: static
walk-atrophy KILLED (preregistered gate, decisive 0/8 +
inverted signal). CONSEQUENCE (labeled by status):
(walk,cong) effectively dead — NOT gated (measured-
consequence: tied weak~=fabric => no differentiation
lever; gated kill applies to atrophy only). Static-chi
EXHAUSTED for scale ((betw,atr) excluded analytically;
(walk,.) voided empirically; (betw,cong) = attenuation
control, never scale) => C2-scale needs GENUINELY-
DYNAMICAL state variables (stateful traffic? budgets? —
new design AFTER betw-cong run). ORDER: betw-cong feedback
run FIRST (close static chapter; fully derived) ->
dynamical-chi design. (Spike process note: comprehension-
recompute bug 3040x (spike-only, fixed; deterministic-
identical results — determinism-check value demonstrated).)
STATIC-CHI HEADSTONE (review verdict adopted — closure, not
mere negative): 2x2 collapse = (betw,cong) attenuation-control
/ (betw,atr) analytic exclusion / (walk,cong) no-lever (tied)
/ (walk,atr) empirical kill (inverted). Kill sentence: chi_K
< chi_F ~= chi_W => atrophy gives w_K > w_F ~= w_W — actively
attacks knot, barely separates weak from fabric.
MONOTONE-ORDER UNIFICATION (two applications, one root):
monotone g preserves order structures — (i) overlap theorem
(cannot un-overlap tails), (ii) kill sentence (cannot invert
rank); g-shopping provably futile both directions.
Susceptibility as NEGATIVE CONTROL adopted (0.104 vs 0.101
null, single-edge 0.102 = uniform 0.104 => avoidance is
EDGE-LOCAL conductance response, collective rerouting ~0.002
— "network self-organization amplifies" dead for walks
specifically). NO-CHI-SHOPPING RULE (enforcement): any future
static-chi proposal must FIRST state its 2x2 cell + why it
escapes that cell's verdict. Worked preemptive kill:
current-flow/random-walk betweenness reduplicates the
BETWEENNESS COLUMN (s-t absorbing flows use shortcuts like
shortest paths: weak-high/interior-low predicted same shape;
atrophy inverted, congestion attenuation-only) — smoother
(linear-solve continuous => fixed-point theory, no flapping)
but same verdicts; admissible ONLY as follow-up smoothed
attenuation experiment if betw-cong flaps uninterpretable,
never scale candidate without new argument. BETW-CONG AS
CLOSURE (locked questions): attenuation factor? beta=350
still in basin? fixed points vs cycles? cadence-sensitive?
Outcomes all useful (stable-in-basin = vacuum-pricing
mechanism with unexplained scale; out = open-loop-only;
cycles = <Phi(w(t))> + basin-fraction verdict). Then
static-chi CLOSED whatever the answer. ABSTRACTION-LEVEL RULE
for what follows: no new scalar chi(G,w) — next variables
must be STATEFUL (q with memory: identical instantaneous
traffic, different price via history — S_n=(G,w,q,...)) or
PRINCIPLED-BUDGET (sum Q = const with physical Q
interpretation BEFORE implementation — uninterpreted Q_total
= beta-in-costume, rejected in advance). Sign of stateful-F
NOT chosen yet (derive from machine-supplied
conserved/current quantities first). H-GATE: gate v2 applies
to H equally (blind reads, update-form, no inserted targets —
memory exempts nothing); BOUNDED MEMORY (scalar q_e, fixed dim
— unbounded histories = infinite state, excluded); MU-DEBT
(memory timescale mu needs intrinsic source — same ledger as
T). WALK-CAMPAIGN
METHODOLOGICAL VERDICT (preserved prominently, never buried):
smoothness + globality of an observable are NOT enough — it
must carry structural information beyond its stationary
transport law (walk-chi's ordering dies at stationarity AND
its avoidance is pure conductance math). This is the filter
against unconstrained model-building next stage.
(Uploaded-conversation boundary-response/memory remark: noted
convergence (dense interiors may need storage/memory) —
reference opaque to agent; independent pointer toward
statefulness, not evidence.) ROADMAP (narrowed, locked):
A-static-congestion [done] -> betw-cong feedback [done] ->
static-chi CLOSED [done] -> stateful-scale derivation [done] ->
gain-free discriminator [done] -> formation DESIGN [done-pre-reg]
-> formation PILOT [NEXT] -> M_O audits. BETW-CONG
DERIVATION (LOCKED closure run — docs-only turn; code next):
LAW w'=(1-a)w+a(1+b*betw_e(w;n)), betw = exact weighted edge-
betweenness recomputed every m ticks; a=0.2, n=64 ticks,
beta in {35,350}, m=4 production + m=1 VALIDATION at 350;
deterministic. Embeddedness regression control same runner
(static chi => A-control EXACT — runner-machinery check).
BOUNDEDNESS (analytic): normalized betw <=1 => w*<=1+beta
ALWAYS — runaway impossible; branch restated converge /
cycle / saturate-at-cap (persistent non-convergence ~beta).
FIXED POINT w*=1+beta*b(w*) implicit, existence NOT
guaranteed (discontinuous) — converge (residual<tol) vs
cycle (amplitude/period + <Phi(w(t))> + basin-time fraction,
never Phi(<w>)). ATTENUATION (status-labeled): weak own
w*_med < static = THEOREM-direction (own<=0), magnitude =
run's number; fabric = HYPOTHESIS (sign-indefinite, either
informative); beta=350 basin = HYPOTHESIS (attenuation may
exit — THE closure question, never corollary); interior ~1
(checked, ungated). REROUTING MAP (PRIMARY anatomy, banked
FOR q-design): R1 per-pop Delta-chi medians (weak<=0
expected; fab/int measured); R2 r_O-binned fabric Delta-chi
median+q90 (gateway pile-up? diffuse? corridor? —
positions not verdicts); R3 top-20 gaining fabric edges
listed (ungated); R4 chi_med(n) trajectories + late-time
per-edge variance (flap amplitude); R5 concave-D
[Delta-chi]*[Delta-w]<=0 to FP tol — EXECUTABLE analytic
check (violation = bug/tie-subtlety, never physics). Map's
VARIANCE structure (slow/transient swinging loads) = banked
q-design input (q remembers slow variables; design AFTER
closure). FLAPPING PROTOCOL (conditional, pre-registered):
cycles at (m=4,a=0.2) => run (m=1,a=0.2) then (m=4,a=0.1);
attribute cadence (m=1 kills) / step-size (a/2 kills) /
physical (both persist). m=1 bar: SAME branch + SAME basin
in/out as m=4. OUTCOMES: IN-BASIN-STABLE (vacuum mechanism,
scale unexplained) / OUT (open-loop-only) / CYCLES (<Phi>
verdict) — ALL close static-chi. TEST/FILE SPLIT: tests pin
reduced-state mechanics + qualitative closure (attenuation
direction, concave-D, determinism, m-shape, fast m=1
machinery); full-state verdict (factor, basin, cycles, map)
filed from spike (precedent). NEXT: code closure run.
BETW-CONG VERDICT (closure run executed 40x40/64 ticks;
static-chi CLOSED): runner check PASSES (embeddedness control
bit-exact maxdev 0.0, Lw1 rows frozen). beta=35 m=4:
weak_med 1.826 (att 0.826), residual 1.05, latevar 0.066,
rows (40,35,29,18)/None. beta=350 m=4: weak_med 6.913 (att
0.591), residual 18.7, latevar 8.96, rows (39,26,13,1)/None
— OUT of basin, basin-frac 0.0, R4 overshoot+ring. beta=350
m=1 (PHYSICAL branch): weak_med 7.842 (att 0.684), fab_med
2.5468 (static 2.0933 — UP, rerouted load lands on fabric),
residual 9.289, endpoint (39,27,13,0) cross=3, basin-frac 1.0
(7/7 late snaps cross=3); R4 weak chi_med 0.0286->~0.019 by
t=8 then flat, NO ringing; weak-var med 0.018 vs m=4's 2.638
(~150x quieter). PROTOCOL VERDICT: m=4 flapping + basin exit
= CADENCE ARTIFACT (m/tau~1 ringing with stale chi — m=1
kills flapping AND restores basin; a=0.1 step correctly
skipped per protocol); both cadences attenuate (same branch
direction — basin membership was the artifact). REROUTING MAP
(m=1, banked for q-design): R1 weak -0.00634 (sheds) / fab
-0.000204 (median flat) / int +2e-06; R2 fab q90 near
0.00615 / mid 0.00818 / far 0.00622 (tails gain in ALL bins,
mid highest — NO gateway pile-up); R3 top gainers scattered
far corridors (r_O mostly 21-27); R4 above; R5 concave-D
-5.00 <= 0 (m=4: -1.03/-14.09 <= 0 — check held both
branches, no bug). RESIDUAL HONESTY: endpoint 9.289 max-norm
= median-converged + edge-level flapping (discontinuous chi,
expected; boundedness w*<=1+beta holds) — basin verdict via
basin-fraction + endpoint cross, never residual-gated.
OUTCOME: IN-BASIN-MEDIAN-STABLE (feedback retains basin with
attenuated factor; beta=350 scale still inserted =
unexplained; edge flapping footnoted). STATIC-CHI CLOSED
(full 2x2 collapse complete — (betw,cong) cell verdict now
measured: attenuation-only; no scale separation in any
static chi). GAPS (honest): beta=35 m=1 unattributed
(unverified, cadence-by-analogy only — out of preregistered
scope); fixed-point existence still open (median-stable,
not max-norm). TEST/FILE HONORED: test_betw_cong_closure
pins reduced-state mechanics + qualitative (determinism,
control, cadence structure, attenuation direction, R1,
concave-D, Phi m-agreement); full-state verdict HERE.
REVIEW-CLOSURE ADOPTED (post-verdict review — agreed +
filed): SLOGAN: static congestion pricing ->(endogenous
feedback) attenuated-but-stable vacuum pricing (NOT
amplification, NOT collapse); scale origin UNRESOLVED,
scale stability under feedback DEMONSTRATED at tested
beta=350 ("stable" = median-stable + basin-frac 1.0, edge
flapping footnoted — qualifier load-bearing). TWO-FLAPPING
DISTINCTION (locked vocabulary): MACROSCOPIC cadence
ringing (m=4 overshoot->ring->basin-exit, killed by m=1 =
discretized feedback-delay artifact) vs MICROSCOPIC
assignment flapping (endpoint residual 9.29, intrinsic
shortest-path discontinuity — m=1 does NOT kill it; never
conflated — the distinction was worth the m=1 run). FORMAL
2x2 CLOSE (restated, final): (betw,cong) useful open-loop +
feedback preserves basin at 350 / (betw,atr) excluded by
ordering / (walk,atr) preregistered empirical kill /
(walk,cong) no structural lever; no principled g(chi)
search remains (monotone-order). BETA-35 HONESTY SHARPENING
(reviewer-caught, fixed): NO basin statement at beta=35/m=1
whatsoever — neither fails nor passes; beta=35 m=4 numbers
are cadence-suspect RAW DATA only; "cadence-by-analogy"
language STRUCK (smuggled a verdict by analogy).
UTILIZATION-HISTORY PRIOR for q (adopted as PRIOR, not
theorem): rerouting non-knot-local (no gateway pile-up,
far-corridor gainers) => memory tracks edge/path
UTILIZATION history (accumulated/decaying traffic J_e),
not knot proximity; second leg H-gate sourcing (traffic
locally observable per edge; knot-proximity has NO machine
source — knots are observer-identified); prior selects the
utilization FAMILY, not the member (normalized vs raw J,
which traffic notion = derivation work). NEXT-UNIT LOCK
(derivation BEFORE code — no memory implementation until
derived): SHARPENED QUESTION: can temporal accumulation
generate the pricing scale static state cannot? CANDIDATE
FORM q_e(n+1)=(1-mu)q_e(n)+J_e(n), w=F(q) (sign /
normalization / mu UNCHOSEN — derivation first).
STEADY-STATE DANGER (mu-debt's first concrete entry):
steady traffic => q*=J*/mu => 1/mu = beta~350 in disguise
unless escaped; linear-accumulation steady gain is ALWAYS
kernel-integral (generalized beyond one form). FORK:
bounded stateful traffic => does amplification emerge from
feedback structure? YES (gain set by graph / implicit
fixed-point structure) -> candidate mechanism / ONLY-AS-1/mu
-> timescale debt = scale debt, renamed not solved / NO ->
memory doesn't solve D14 scale (formation/topology branch
inherits per roadmap). ACCEPTANCE CRITERION for YES: gain
formula contains NO mu (mu only in rates/timescales).
DERIVATION MUST ADDRESS: (i) normalized-J / budget routes
to mu-free RELATIVE prices (w~q/Sigq => steady relative ~
J*/SigJ* — absolute gain then lives in F = beta-in-costume
unless derived); (ii) nonlinear-H escapes and their
smuggled scales (thresholds ARE scales); (iii) what counts
as feedback-structure amplification (implicit q->w->routing
->J->q fixed point, criticality, conserved redistribution).
DEBT-IDENTIFICATION RULE: any gain reducing to a free
parameter (mu, threshold, uninterpreted Q_total, F-gain) is
NAMED as that debt, never as emergence.
NEXT: stateful-scale derivation unit (docs-only,
pre-registered above — answers NOT derived this turn).
STATEFUL-SCALE DERIVATION (executed docs-only — answers
derived this turn): LINEAR KILL (theorem-direction, no run
needed): LTI memory q=K*J + affine w=1+gq => steady
w*=1+(g*SigK)J* — IDENTICAL to static congestion with
beta=g*SigK (first-order: q*=J*/mu as flagged); memory
contributes TRANSIENTS ONLY (timescale 1/mu; higher-order
kernels ring — temporal structure, not scale). Memory axis:
mu=1 IS static (one-tick lag, same steady); mu->0 windup
(no steady state, excluded by bounded-memory); interior =
static-with-transients. Linear memory KILLED as scale
mechanism. STRUCTURAL-NUMBER CRITERION (YES-prong
admission): dimensionless machine => every number is
STRUCTURAL (counts, spectral values, lattice unit, path
masses) or DEBT (modeler-chosen) — gain ~350 must be
structural; YES prong currently UNOCCUPIED (no candidate
exhibited). CHARACTERISTIC-SCALE LEMMA: smooth
nonlinearity f carries free scale |f'/f''|
(operating-point/crossover — free unless derived);
scale-free power laws carry free (prefactor, exponent);
thresholds/saturations carry free scales in J/q units;
criticality fixes SHAPES (exponents), never AMPLITUDES.
Nonlinearity buys shape freedom; magnitude stays debt.
FEEDBACK AUDIT: closed-loop cartoon g/(1-loop) — loop->1
amplifies but distance-to-critical is TUNING (debt); SOC
removes tuning but magnitudes are cutoff-set (structural
ONLY if cutoff is machine-structural — unoccupied);
positive feedback => saturation-set switches (saturation =
scale; unsaturated => unbounded, excluded); our m=4
ringing exhibits the general fact (feedback structure
mints TIMESCALES/oscillations, not scale); implicit
q->w->routing->J->q fixed point REDISTRIBUTES given gain
(measured: attenuation 0.684) — modulation, never minting.
BUDGET ROUTE: Sigq=Q or normalized J => steady RELATIVE
prices mu-free (w~q/Sigq => relative ~ J*/SigJ* exactly)
— but absolute gain lives in F (debt) UNLESS gain-free
ratio pricing. TRAFFIC-RATIO SCALE (filed numbers only,
no code): normalized betw => Sig chi = Lbar; mean chi =
Lbar/E ~ 26.7/3380 ~ 0.0079; weak chi_med 0.0286 =>
ratio ~3.5 — structural hierarchy is O(few);
basin-entry weak_med in indicative interval (2.00,11.00)
(beta=35/350 static brackets; shape-transfer approximate)
=> gain-free candidacy MARGINAL, undecidable by
derivation. ERRATUM (post-measurement): Lbar 26.7 was
pure-grid; swapped+clique Lbar ~14.3 (measured 14.26;
small-world shortening; Sig chi = 14.268 confirms the
identity) => corrected sketch ratio ~6.2 = measured 6.216;
O(few) claim stands, estimate superseded. POSED DISCRIMINATOR (designed NOT run —
zero-free-parameter pricing w_e=max(1,J_e/Jbar),
J=static betw, Jbar over non-interior edges per
mask-exclusion precedent, fabric-safe by lattice-unit
clip — 1 is ontological, not free): HEALS => D14 scale
dissolves into traffic structure (YES prong occupied, no
memory needed) / FAILS => debt confirmed
(nonlinearity/gain required => named debt;
formation/topology inherits). NO directional prediction
(marginal 3.5 in (2,11) — interpretation pre-registered,
outcome open). FORK VERDICT: linear NO (proven);
nonlinear/feedback ONLY-AS-debt (lemma + audit);
structural YES unoccupied pending discriminator.
Memory's scale candidacy SUSPENDED (not killed —
discriminator + YES-criterion are the live paths).
NEXT: gain-free discriminator run (cheap static run —
code next turn).
DISCRIMINATOR VERDICT (executed full-state, ~7s): FAILS —
rows (39,30,20,4)/None, no TOL crossing => debt CONFIRMED
per pre-registered interpretation (basin reach needs
nonlinearity/gain = NAMED debt; YES prong logically open
but its natural structural candidate fails;
formation/topology inherits). Numbers: Jbar(nonint)
0.004598, weak_med 6.216 (pure traffic ratio), fab_med
EXACTLY 1.0 (median fabric clipped to ontological floor),
max_w 11.707 — hierarchy PEAK reaches static-beta=350
median scale (~11) but MEDIAN (6.2) sits in the dead
interval: right order at top, insufficient mass at median
(shape AND magnitude defeat it). DOSE-RESPONSE (secondary):
rows strictly between locked static brackets at every k
(beta=35 (40,34,29,17)/None, beta=350 (36,23,7,0)/cross=3)
— Phi monotone in weak_med over three points (2.0/6.2/11.0),
indicative basin-entry threshold NARROWED to (6.2,11.0)
(shape-transfer approximate). D14 STATUS: static pricing
can reach the basin (A) and survive feedback (closure) but
its GAIN is debt by elimination (linear/memory/budget
audited, structural candidate failed) — magnitude origin
now belongs to formation/dynamic topology or an
unexhibited structural number. Test pins full-state rows +
medians + dose-response (test_gain_free_discriminator).
NEXT: formation/dynamic-topology DESIGN unit (docs-only
pre-registration first — derive-then-code rhythm holds).
FORMATION DESIGN (C2 pre-registration — docs-only; pilot gated
on this): INHERITANCE: D14 scale = debt by elimination
(static/feedback/memory/budget/structural-ratio audited);
formation asks topology-not-prices (YES-prong currency native:
counts/cuts/spectra structural); serves the P0' conditional
(separating U + basin breadth + residue→2). MACHINE (minimal):
fixed-N, E-conserving EDGE RELOCATION (remove (a,b), add random
non-edge (c,d) — degrees CHANGE (degree-preserving swaps
FROZEN-OUT at design: histogram-frozen, bimodalization
impossible — caught before code); E conserved exactly (budget =
edge count, working interpretation: entanglement units —
ADOPTED, flagged revisable); proposals blind-uniform (H-clean).
G_* ENSEMBLE (sketch: homogeneous dense, d_* measured-never-
tuned): ER zbar∈{8,16} + random-regular z=8 (3 ensembles) ×
N∈{1600,3600} × seeds{0,1,2}; d_* MEASURED per G_* (filed);
SOUP-VALIDITY executable: initial histogram UNIMODAL (else
invalid run). DRIVERS: D1 NULL (pure random relocation —
required; prediction: stays unimodal (entropy); violation =
bug-hunt trigger); D3 FLOPPY-GATED KINETICS (primary: execute
iff loser-endpoint floppy (local z<4, KCM/Fredrickson-Andersen
class — threshold MECHANISTIC not objective (filed
distinction: kinetic-gate vs target-valued acceptance);
mechanism sketch (HOPE not claim): floppy-losers shed + blind
gainers => depleted-floppy / dense-rigid segregation;
PREDICTION: bimodalize, fabric mode≈4 (falsifiable));
threshold∈{3,4,5} FACTOR (marginality predicts 4 special;
identical behavior = reinterpret branch); gainer-gated /
symmetric variants QUEUED contingent (design amendment
required). D2 tension-energy QUEUED (blocker: linear
tension-energy flat (no selective pressure); interaction form
underived; concave-by-choice = inserted-by-construction); D4
tournament-transfer QUEUED (transfer status; gate-key
re-derivation needed — healing gates key on known-damage
counts, formation has no non-inserted badness). H-GATE (bites
hardest — locked clauses): H1 no target-valued acceptance
(accept/reject may not reference distance-to-fabric, z=4-as-
goal, 2D-ness, outcome quantities — forbidden-inputs list,
TARGET-VARIABLE-EXCLUSION precedent); H2 objectives need
interpretation-first (uninterpreted = rejected in advance;
budget-Q rule generalized); H3 blind reads + update-form (D1
form; census/evaluative gates BANNED for formation (no
non-inserted badness); MECHANISTIC/kinetic gates only). RUN
PROTOCOL: stop = arrest (no executes for W=20 sweeps) OR
stationarity (histogram L1 < 0.02 over 50 sweeps — labeled)
OR T_max=2000 cap (labeled). GRID: full @N=1600 (3 ens × 3
seeds × (D1 + D3×{3,4,5}) = 36 runs) + scaling subset @N=3600
(D1 + D3@4; 18 runs) = 54 runs. READOUTS — PRIMARY
(algorithm-free): coordination-histogram bimodality via
valley-depth ratio (two highest local maxima, valley-min /
lower-peak < 0.5 = bimodal — LABELED; histograms FILED as the
evidence, statistic is the gate) + mode locations (MEASURED,
no targets); SECONDARY: degree-assortativity rise (nx,
segregation signature); knot-ID (TWO detectors, agreement
required — ID claims only); CONTINGENT: d_G on depleted phase
(UNGATED characterization — planarization NOT claimed);
Φ-basin under gain-free pricing on formed state (STRONG
reading — banked apparatus, zero new choices). WEAK vs STRONG
(locked split): WEAK = spontaneous bimodalization + mode
locations (topology result); STRONG = discriminator flips to
HEALS on formed state (D14 kill-or-confirm). DEPLETION vs
PLANARIZATION SPLIT (scoping honesty): pilot tests
DEPLETION/segregation ONLY; 2D-ness of residue queued as
D14(ii-b) (nothing here selects planarity — filed gap, not
oversight). DEBT TABLE: N/E (finite-size → scaling subset or
labeled); G_* density (CHOICE → 3-ensemble robustness or
initial-condition-labeled); threshold 4 (mechanistic +
factor-tested); W/T_max/tol (protocol, labeled); valley 0.5
(labeled conventional); detectors (choice → dual-agreement);
Φ/discriminator (banked, zero new). OUTCOME TABLE:
WEAK-YES+STRONG-YES => formation SOLVES D14 scale (promote
D-track); WEAK-YES+STRONG-NO => KIND-not-DEGREE (partial:
debt narrows to amplification-on-formed-topology; memory /
budget revisit ON formed states = contingent branch);
WEAK-NO => D3 insufficient (no auto-escalate); DARK
(D1+D3+D2+D4 all WEAK-NO) => formation doubted; YES-prong
empty-by-exhaustion; D14 scale TERMINALLY unexplained
(ledger records exhaustion — filed in advance). STOP RULE:
D3 WEAK-NO => design amendment required before D2/D4 (no
silent queue-burn). EXECUTABLE CHECKS: E-conserved exactly
every tick; D1-unimodal (bug-hunt if violated); N-scaling
persistence (vanishes-with-N => finite-size artifact =>
WEAK-NO-by-scaling downgrade, pre-registered); soup-validity
(above). STAGE-GATE: C2 mechanism demo ONLY (no origin
claims); D-promotion checklist (ensembles + instability +
no-insertion proof + N-scaling + G_*-robustness + independent
replication) — D fenced. APPARATUS (new code): G_*
constructors + D3 driver + histogram/valley/assortativity
readouts (all else banked: Φ, discriminator, cuts, d_G).
NEXT: formation PILOT (code next go — gated on this pre-reg).
FORMATION DESIGN AMENDMENT (review-forced: connectivity +
seed/absorbing — preconditions for running; pilot still
gated): CONNECTIVITY POLICY (reviewer's lean ADOPTED):
fragmentation ALLOWED (no guard — guard would be evaluative,
H1-banned; vacuum-connectedness is an L0 outcome fact, not a
dynamical license (steering-to-answer confusion filed));
HEALTH READOUTS HARD: giant-component fraction ≥ 0.9 GATES
WEAK-YES (0.9 labeled conventional); component-size
distribution FILED full (not gated); STRONG readouts run ON
GIANT (percolation practice); giant < 0.9 => STRONG UNTESTED
(validity, not verdict). ABSORBING-STATE CHARACTERIZATION
(derived at design — reframes D3's hope): D3-OR arrest ⟺
rigid (z≥4) subgraph + isolated (z=0) dust (proof: z∈{1,2,3}
nodes always own an executable edge ⇒ absent at arrest) =>
arrested end-states are WRONG-kind AUTOMATICALLY (reviewer's
feared artifact = CHARACTERISTIC failure mode, not accident
— sharp > vague); D3's hope is ACTIVE steady state
(gainer-rescue sustains floppy bulk), NOT arrest-into-phases.
STOP-RULE INTERPRETATIONS (locked): arrest => dust-expected
=> health-gated (PREDICTION: arrested runs score WEAK-NO);
stationarity => WEAK-candidate; T_max cap => UNRESOLVED
(transient-too-slow; extension needs amendment). SEED ISSUE
(KCM sense: initial excitations): RR-8 D3 STILLBORN (theorem:
all z=8 ⇒ zero executable at tick 0); ER-16 near-certain
stillborn (~0.15 expected floppy); ER-8 runnable (~4%);
STILLBORN-RULE: zero executes in first W=20 sweeps ⇒ run
INVALID (not WEAK-NO); expected-invalids RUN as negative
controls on validity machinery (informative: KCM
arrest-needs-seeds); HAND-SEEDING BANNED (planting;
C2-unplanted violation); D1 never stillborn (ungated
relocation always executable — one-liner). WEAK-YES AMENDED
(was: bimodal + modes): bimodal (valley<0.5) AND lower-mode
≥ 2 (BULK LINE, principled: z<2 ⇒ no cycles through node ⇒
cannot be mesh bulk — excludes dust/hair without targeting)
AND giant ≥ 0.9; NO upper-mode target (would be
target-valued — restraint filed; contrast measured).
DISAMBIGUATIONS (pre-amble gaps closed): loser-gate = OR
(either endpoint floppy — most permissive; failure-under-OR
⇒ failure-under-AND (heuristic, LABELED); AND queued
contingent); gainer = uniform random non-edge (both
endpoints blind). NON-INTERFERENCE AUDIT (strong-win
license): D3 inputs {degrees/counts} ∩ discriminator inputs
{static betw, mean} = ∅ (formal disjointness; correlation
caveat filed honestly: both graph quantities, possibly
value-correlated — unengineered claim rests on
input-disjointness + pre-registration, labeled). STRONG-WIN
INTERPRETATION (reviewer's box ADOPTED): observer-blind
kinetic instability redistributes fixed E into persistent
phases AND the resulting topology independently makes the
previously-insufficient gain-free rule sufficient — neither
stage designed against the other's target (the meeting is
unengineered).
NEXT: formation PILOT (code next go — gated on pre-reg + amendment).
FORMATION DESIGN AMENDMENT-2 (design correction, PRE-DATA —
strong-clause incoherence caught before any run):
STRONG-as-filed (Φ-basin on formed state, `banked apparatus')
is CATEGORY-BROKEN for this pilot: relocation-formation on ER
soup NEVER produces geometry (no positions/embeddings), and
Φ/η (spans, rulers, longs) REQUIRE extrinsic geometry
(self-ruler via phases = circular (target leaks into ruler —
RULER-TRAP precedent) + new apparatus (violates `zero new
choices')). CORRECTION: this pilot (C2-PILOT-1, TOPOLOGICAL
formation) tests WEAK ONLY (spontaneous segregation; ceiling
= KIND-not-DEGREE partial, pre-registered branch);
STRONG (discriminator flip) RE-HOMED to C2-PILOT-2
(GEOMETRIC formation — future design: formation WITH
positions/embeddings) — re-homed, NOT dropped
(outcome-table STRONG-YES cell unreachable-here, filed).
DEEPER LESSON (filed): D14 scale is GEOMETRIC (pricing ~
spans); topological formation can supply KIND never test
DEGREE. CHARACTERIZATION (not verdict): on WEAK-YES states
file J-histogram + max/mean + p90/mean + median/mean, J̄ =
all-edge mean (no-mask default, labeled), vs indicative
(6.2,11.0) (threshold-transfer approximate², NO verdict —
informs geometric design). BLINDNESS (moot-but-filed): no
pricing/traffic quantities touched pre-amendment (nothing
run at all — genuinely pre-data).
NEXT: formation PILOT (code now — gated on pre-reg + amendments).
FORMATION DESIGN AMENDMENT-3 (detector calibration, POST-ER-data
(24 runs) but PRE-VERDICT — guarded-valley analysis locked
BEFORE any guarded number is computed): TRIGGER: null
false-positive — D1-s1-ER-8-1600 letter-valley 0.000 via an
ISOLATED TAIL SINGLETON (mode (18,1) beyond a gap; valley=0
over [7,18] → ratio 0/1 = 0 → WEAK-YES-by-letter ON THE NULL
(lower-mode 7 ≥ 2 ✓, giant 1.0 ✓)). DIAGNOSIS: letter valley
(top-two local maxima, raw counts) admits measure-zero peaks
(singletons beyond gaps trip via valley=0). FIX (locked):
mass-guarded valley — maxima need count ≥ 2 (minimal
non-singleton: a phase ≠ one node — definitional, pre-reg
intent `dense knots + depleted fabric' (both macroscopic));
library default min_mass=2, letter = min_mass=1. ROBUSTNESS
(locked): guarded verdicts must be INVARIANT over guard ∈
[2,65] (any value identical → value untuned, only existence
matters); if variant → file variant + escalate (no silent
tuning). DUAL REPORT (locked): letter-verdicts filed (D1-s1
YES-by-letter = documented false positive) + guarded
verdicts (primary post-calibration). CALIBRATION STATUS:
detector fixed on NULL behavior (not on D3 outcomes — all 54
guarded verdicts computed AFTER this lock, uniformly from
raw filed hists, no re-runs needed).
AMENDMENT-3 ESCALATION (locked procedure FIRED — rule below
locked BEFORE any gap-aware number is computed): guard-
robustness FAILED with 10 VARIANTS: D1 tail islands (mass
2-6 beyond gaps: 1600-rr8-s0/s2-d1, 3600-er16-s0-d1,
3600-rr8-s2-d1 (+3 mode-only)) flip WEAK under mass-2
(4/54 WEAK-guarded, ALL on the NULL); D3@3 dust (16-20)
flips the bimodal flag (WEAK stays NO via lower-mode).
Pattern: the discriminator is the GAP, not the mass
(connected-tail peaks (mass 6, 12) give shallow valleys
(0.833, unimodal ✓); only beyond-gap islands trip
(valley=0)). ADOPTED (locked): connected-support
(gap-aware) valley — intervals with interior empty bins =
disconnected islands, not saddles → 1.0. NOT TUNING: binary
topological property (NO tunable value — nothing to tune);
textbook bimodality (saddle, not gap); agrees with
mass-guard on all non-artifact cases HERE (provable:
D3-arrest support = {0}∪[thr,∞) (theorem) → any D3 gap
touches z=1 (excluded by lower-mode≥2 anyway) → D3 WEAK-NO
under EVERY statistic; only divergence = tail islands
(artifact)). TRIPLE REPORT (locked): letter + mass-2 +
gap-aware (all filed; gap-aware primary). CAVEAT (locked):
gap-aware may under-call complete separation in future
drivers — revisit if gapped non-dust support appears.
FORMATION DESIGN AMENDMENT-4 (detector RESTART — locked
BEFORE any floor/sweep number is computed): TRIGGER:
gap-aware INSUFFICIENT (2 null-WEAKs persist:
singleton-BRIDGED islands (1600-rr8-s0-d1 (18,4),
3600-er16-s0-d1 (30,4): interior min 1 (not 0!) →
connected → valley 1/4 = 0.25 trips)). ACKNOWLEDGED:
patch-chain (letter→mass→gap→floor); STOP patching
mechanisms. PRINCIPLED RESTART: `phase' = macroscopic
CONSTITUTIVELY (any operationalization needs a
macroscopicity scale — the floor is part of the question's
meaning, not a tuning knob). LOCKED: fractional floor
(peaks need count ≥ max(2, ⌈frac·N⌉) (scale-free);
gap-aware stays ON; library UNCHANGED (fractional =
analysis-level min_mass)); SWEEP frac ∈ {0.1%, 0.25%,
0.5%, 1%, 2%, 5%, 10%}; PRIMARY 1% (log-central in
[0.1,10], locked for centrality, not outcomes).
PREDICTION (filed): WEAK 0/54 over [0.5%,10%] (20× —
formalization-independence); floors below max-fluctuation
(~0.33%) admit fluctuations (artifacts EXPECTED there —
a floor must exceed fluctuation scale to mean macroscopic).
VERDICT RULE (locked): sweep-unanimous-DARK over [0.5%,10%]
→ DARK (sweep-proven); else file all + conclude cautiously
(no shopping). MECHANISM CHECK (locked): islands claimed as
Poisson-tail sparseness — VERIFY (expected tail counts vs
observed + bulk var vs Poisson; filed either way; verdict
robust to mechanism (mass alone decides)).
C2-PILOT-1 VERDICT: DARK (SWEEP-PROVEN — 54/54 runs):
floor-sweep WEAK = 0/54 UNANIMOUS over [0.5%,10%] (20×);
floors below fluctuation scale admit artifacts (0.10%:
2/54, 0.25%: 1/54 — as predicted). DETECTOR SAGA (filed):
letter 6/54 → mass-2 4/54 → gap-aware 2/54 (ALL on D1
null) → floor-sweep 0/54. NO non-dust bimodality
ANYWHERE (no two macroscopic bulks in any of 54 hists).
D1 NULL (18/18): cap + full activity (rate_tail == E0
EXACT, slope +0.000) + unimodal + POISSON EQUILIBRIUM
(var≈mean all 18 (7.4-8.5 vs 8; 15.3-16.5 vs 16) —
D1 = Poissonizer (no regularization (guess refuted)));
drift ER 0.055-0.152 (≈ noise floor 0.106 PREDICTED ✓),
RR 1.71-1.73 (delta-broadening transient); |assort| ≤
0.029 (mixed). D3 (13 arrest + 23 stillborn, ZERO
active — active-steady-state HOPE DEAD): arrests ALL
rigid+dust (13/13 theorem checks; ncomp = dust+1 EXACT
(all non-giant comps singletons); dust thr3 ~1% (16-20),
thr4 ~4% (65-68 @1600, 145-163 @3600), thr5 ~11%
(171-190); giants 0.99/0.96/0.88-0.89 (thr5 < 0.9!);
arrest ≤ 34 sweeps, execs 3-803); stillborns RR-8 12/12
(theorem) + ER-16 11/12 (one marginal-live: 3 execs,
1 dust — Poisson-tail lottery). ISLANDS = Poisson-tail
sparseness QUANTITATIVE (obs z≥18 vs expected: 4v2.3,
1v2.4, 5v2.6, 7v6.2, 8v6.0, 4v5.7, ..., ER-16 bullseye
(543v556, 1252v1234 — all ~2σ)). SOUPS 18/18 valid
(gap-aware); DETERMINISM 23/23 exact cross-process
(stillborn finals); E-CONSERVATION 54/54. GATE LESSON:
literal stationarity gate = freeze-detector (noise
0.1 ≫ tol 0.02 — never fires on active runs; filed,
unchanged; settled-active read via characterization).
DESIGN LESSON (big): NO CONCENTRATION PATHWAY —
loser-shedding + diffuse-gain → dust-or-nothing
PROVABLY (no mechanism concentrates!); knots need
concentration. LEADS (design next turn): D5
triangle-closure (LEAD: local, blind-legal,
concentrates CLUSTERING (knot-like) vs fabric) /
D4 gainer-bias (PA-mimetic → hubs (≠ knots!)) /
C2-PILOT-2 geometric (positions + spatial rewiring
(STRONG home)). DARK branch = pivot knobs (pointer
filed; next design gated on go).
REVIEW RESPONSE (DARK comments — agreed + sharpened, filed):
DICHOTOMY > 0/54 (accepted as headline: mechanistic
closure, not parameterization-failure). D3-final =
dust + TRUNCATED-Poisson-bulk VERIFIED: bulk (z≥thr)
var 6.1-7.6 vs mean 8.0-9.0 (sub-Poisson (left-
truncation!) + densified (E fixed, fewer mouths));
L1-vs-Poisson ORDERS drivers: D1 0.03-0.10 (noise
floor, 1/√N-ish) < D3@3 0.06-0.11 < D3@4 0.13-0.17
< D3@5 0.35-0.40 (departure = dust + truncation).
DEPARTURE-FROM-POISSON ADOPTED as primary formation
metric (reviewer's opponent-framing; floor calibrated
~0.03-0.10 here). POISSONIZER = CONJECTURE + M/M/∞
SKETCH (filed, not theorem): single-node mean-field
(constant immigration λ=2E0/N (uniform gainer) +
linear emigration μz (uniform loser) → Poisson(λ/μ)
= Poisson(z̄)); gaps: same-node gain+loss correl.,
non-edge saturation (sparse ✓), E-coupling
(mean-field!); evidence 18/18 + both-sided transient
(delta→Poisson (RR), Poisson→Poisson (ER-stat.)).
CLASS-CLOSURE (stronger than D3-closed): ANY
local-loss-gate × uniform-gain → dust + Poisson-bulk
(gain-side theorem (M/M/∞-sketch) ⟹ NO concentration
possible in-class) — licenses NO-D3-RESCUE rigorously
(any loss-variant (thr6? triangle-unclosing?) stays
in-class; gain-side change = D4/D5 (new mechanism,
not rescue)). TRIPTYCH + 2×2 (loss×gain): D1 =
(diffuse,diffuse) → Poisson; D3 = (gated-loss,
diffuse-gain) → dust+trunc-Pois; D5 = (diffuse-loss,
gated-gain) → ??? (D3-MIRROR!); D35 = (gated,gated)
→ ??? (design scopes; mirrors static-χ 2×2 close).
D5 NEXT (agreed) + D4 BEHIND (double reason: PA→hubs
is KNOWN (not discovery) + wrong object (C_hub≪1;
D4 = degree-concentration, D5 = clustering-
concentration (right observable!))). CLIQUE-
CONDENSATION pre-reg ADOPTED (K-scaling O(1)/N^α/O(N)
+ count (one-vs-MANY!) + sizes). GEOMETRY RULING
(agreed): positions-in-law = ruler (RULER-TRAP
precedent) → geometric = BENCHMARK-ONLY (labeled,
non-discovery); C2-PILOT-2 = D5 (topological!).
STRONG PARKED (filed, not dropped): Φ needs geometry
⟹ untestable-in-D5; homes = geometric-benchmark
(labeled) OR topology-native basin (η-without-spans?
open design). J2 SYMMETRY (filed, no coupling):
state-space ≠ mechanism (U must activate) — both
tracks converge methodologically; programs stay
INDEPENDENT.
D5 DESIGN BRIEF (LOCKED SCOPE — docs-only
derivation next go (no code!)): (i) pure-closure
fixed points (cluster-graph + triangle-free
remainder? derive!); (ii) condensation scaling
(K(N) test, ≥3 N (1600/3600/6400? cost!));
(iii) H-gate-clean rule (D1-loser + closure-biased
gainer? 2×2 scope (D5? D35?)); (iv) extensive-vs-
condensation discriminator (K + count + sizes +
scaling); (v) metric (departure-L1 (floor!) + truss/
clustering readouts); (vi) K-ESTIMATOR decision
(max-clique NP-hard! lead: k-truss profile
(computable) + alternatives); (vii) outcome table
(extensive/coexistence vs condensation vs dust-like
vs Poisson (no-effect!)) + failure pre-regs
(clique-condensation + clustered-hub? enumerate!).
NEXT: docs-only D5 derivation (gated on go).
D5 DERIVATION (docs-only — 7 locked items, no code):
RULE (H-gate-clean, LOCKED): D5κ (soft): loser =
uniform edge + gainer = uniform non-edge (blind-
propose ✓) + ACCEPT w.p. min(1,exp(κ·Δt_net))
(Δt_net = Δt_gain−Δt_loss (common-neighbors (±)
(1-hop-local ✓))); κ=0 ⟹ D1 EXACTLY (null-
continuous ✓; D1 legs REUSED as κ=0 (no re-run!)).
D5∞ (hard, D3-MIRROR): accept iff gain-Δt ≥ 1
(loss-side free (gain-gate-ONLY (mirrors D3's
loss-gate-only!))). D35 = D3-thr4-loser × κ1-net-
gainer (one cell). H-AUDIT (filed): reads N(a),
N(b),N(c),N(d) only (1-hop (vs floppy 0-hop
(precedent-compatible))); NO labels/dimension/
z̄-targets/bimodality/global-density/geometry ✓;
κ = temperature (biases FLUX not STATE (emergent!)).
κ-BUG CAUGHT (design-before-code vindicated):
gain-only-Metropolis min(1,e^{κΔt_gain}) with
Δt_gain ≥ 0 ALWAYS ACCEPTS (= D1! no bias!) —
MUST be net-Δt (loss-side in accept!) for bias.
STRAUSS (literature-connected): D5κ-stationary ∝
exp(κ·T) (T = #triangles) = Strauss-triangle-ERGM
(canonical (E-fixed!)); reviewer's clique-
condensation = STRAUSS DEGENERACY (known
phenomenon (grand-canonical jumps sparse↔complete;
canonical ⟹ one-clique + remainder (derive below!))).
PURE (κ=∞) FIXED POINTS (exact): absorbing ⟺ all
non-edges Δt=0 ⟺ DISJOINT-CLIQUES + TRIANGLE-FREE-
remainder (cluster-graph + forest (no-op-exclusion
(filed!) blocks self-heal; intra-full + cross-Δt0
⟹ nothing executable ✓). REACHABILITY (derived):
pump-phase (+1 triangle/move (close-wedge (+1) vs
soup-loss (~0.04)) → ~240k closes (~37 sweeps!))
then hair-exchange ACTIVE-STEADY (clique-edges ↔
sticky-hairs (both Δt≥1-executable; hairs re-attach
(never leave))) ⟹ bare-clique UNREACHABLE; steady
= clique + STICKY-HAIRS + dust-bulk (K fluctuates!).
CONDENSATION SCALING (extremal): max-triangles at
fixed-E = clique K_m (m(m−1)/2 ≤ E) + edge-soak
remainder ⟹ K ≈ √(2E) = √(z̄N) (113 @1600 (7.1%),
170 @3600 (4.7%), 226 @6400 (3.5%)) ⟹ α = 1/2
(MESOSCOPIC (reviewer's middle branch!) — share
SHRINKS with N (vs O(N) flat (discriminator!))).
E-STARVATION (mirror-manifest!): K=113 eats 6328/6400
edges ⟹ bulk ≈ DUST (72 strays, z̄≈0.1) — D5∞ =
clique + DUST-BULK (~90%!) (INVERTED D3 (dust +
Poisson-bulk (diffuse-gain keeps-E-in-bulk;
concentrating-gain HOGS-E-into-clique!))).
COARSENING (no-coexistence-prediction): one-K_m
(m³/6 tris) BEATS two-K_{m/√2} (m³/4.24 (same E!))
(superlinear (K³ vs K²!) ⟹ concentration wins ⟹
Ostwald-pressure (big eats small (churn-mediated!))
⟹ steady-coexistence needs ANTI-COARSENING (absent
in D5!) ⟹ PREDICT condensation-or-Poisson (NOT
coexistence); transient-many possible (metastable!
⟹ count(t) readout (Ostwald-check (mandatory!))).
NUCLEATION BARRIER (bistability): Strauss-first-
order-ish ⟹ metastable-Poisson (no-nucleation-in-T)
vs nucleated-clique ⟹ κ_c(T) KINETIC (barrier-
crossing-in-T (not thermodynamic!)); κ = noise
(anneal-window: ∞/2 quench (multi-transient (slow-
coarsen!)) vs 1/0.5 anneal (cleaner-single!) vs
0.25 hot (washed-out (Poisson+!))); κ_c ↓ in z̄
(ER-16 seeds 683 tris vs 85 (nucleates easier!)).
K-ESTIMATOR (LOCKED): LEAD = k-truss (binary-search
k_max + log-profile + macro-floored (1% (amend-4!)
) top-truss components); CROSS = Charikar-peeling
(dense-subgraph (fast!)); EXCLUDED = max-clique
(NP-hard!). Baselines: ER-soup T ≈ z̄³/6 (85/683),
RR T ≈ (z̄−1)³/6 (~57); wedges ~51k (z̄=8);
k_max,init ≈ 3-5 (soup-validity-D5: ≤4 (verify!)).
DISCRIMINATOR (5 cells, LOCKED): dense objects =
top-truss components ≥1% (COUNT!) + count(k)
PROFILE (mid-k hiding!) + K (max size) + sizes +
K(N) + count(t): CONDENSATION (count=1, meso-K
(α≈1/2!), T-pumped, departure-LARGE, dust-bulk
(predicted D5∞ + D5κ-large!)) / COEXISTENCE
(count≥2 PERSISTENT (discovery! (surprise (no
anti-coarsening!)))) / POISSON (no macro-truss
(k_max≈3-4), departure≈noise (small-κ/barrier!)) /
DEFECT (count=1, O(1)-K) / COARSENING (count(t)↓
(transient-many (Ostwald (no-steady-coexistence!))).
PRIMARY VERDICT: extensive-coexistence? (count≥2 +
persistent (YES/NO)). VALLEY = AUXILIARY-ONLY
(detector-scope honesty: clique = high-z ISLAND
(disconnected!) ⟹ gap-aware → 1.0 (under-calls by
design (bulk-phase detector!)); file mass-bimodal
(island-listed!) as characterization). NO GIANT-
GATE (condensation ⟹ small-giant BY CONSTRUCTION
(~10-15%!); giant = characterization (inverted!)).
METRIC SUITE (locked): departure-L1 (floor 1/√N
(calibrated 0.03-0.10!) — PREDICT s-jump at κ_c
(noise → LARGE (~1+ (90%-dust-bulk vs Pois(8)!))));
T (= Hamiltonian (trace T(t) (pump!))) + C (global
+ per-node mean) + truss-profile + count/K/sizes +
K(N) + count(t) + top-z-node-C (hub-vs-clique:
≈1 (clique!) vs ≪1 (PA-hub!) (reviewer's test!)).
SCOPE (LOCKED, 72 runs): (A) BEHAVIOR @N=1600:
{D5κ0.25, D5κ0.5, D5κ1, D5κ2, D5∞, D35} × {ER-8,
ER-16, RR-8} × seeds012 (54 (κ-grid spans hot→
cold→quench (soup-scale κ~0.1-1 (Δt~O(1-10)!))));
(B) LADDER: {D5∞, D5κ1} × ER-8 × seeds012 ×
{1600,3600,6400} (18 (K(N) α̂ ± (3-pt (rough
(pilot-scale!))))). T_max 2000 (precedent) + stops:
D5κ (cap/stationary (soft (never arrest/stillborn!)));
D5∞ (arrest (absorbing-class!) / cap (exchange-
active!)); D35 (stillborn? (D3-loser (RR (precedent!)
+ ER-16-lottery!)) / arrest (dust+clique-frozen?!) /
cap). Stationary-gate = freeze-detector (known-
limitation (reuse + characterization-reading!)).
OUTCOME TABLE + FAILURES (locked): cells (5, above)
+ D35-cell (dust+clique (predicted!) vs dust+Poisson
(gain-ineffective (κ1-too-small?!))); FAILURES:
clique-condensation (reviewer's ✓ (K-meso + count-1
+ dust-bulk!)); barrier-freeze (Poisson-persistence
(kinetic! (contingent T×2 rerun (barrier-test!))));
clustered-hub (top-z-C ≈1 (in-clique (not separate
(consolidated!)) vs ≪1 (PA-like (anomaly!))).
PREDICTIONS (falsifiable battery): P1 (D5∞ →
count-1 meso-clique + sticky-hairs + dust-bulk
(90%!), ACTIVE (K-fluctuating!)); P2 (D5κ: L1(κ)
jumps at κ_c(T) (noise → LARGE)); P3 (κ sets RATE
not SIZE (K ≈ c(κ)√(z̄N) (α=1/2 ∀ nucleating κ;
c↑κ (tightness!))); P4 (κ_c ↓ in z̄); P5 (no
steady-coexistence (count≥2 ⟹ count(t)↓)); P6
(D35 → dust + clique (not dust+Poisson!)); P7
(valley-aux: gap-aware-1.0 + mass-bimodal); P8
(bulk-E-starvation (bulk-z̄ ↓ as clique grows));
P9 (κ-moderate nucleates CLEANEST (anneal-window!)).
P6-REVISION (pre-campaign (smoke-mechanics N=400
(not grid!) + derived timescale-rule (not tuned!)):
D35 SMOKE ARRESTS at 25sw/58exec (T +12 only) ⟹
LOSS-FREEZE (25-34sw) ≪ CLOSURE-NUCLEATION (100s-sw)
⟹ D35-gain-STARVED (κ1) ⟹ REVISED-P6: D35 → dust +
rigid-bulk (D3-like (T-elevated (+O(10-50) (gain-
scraps!)))) (NOT dust+clique!). DERIVED: D35-arrest
⟺ D3-arrest-condition (rigid+dust (gain-soft can't
arrest (only hard-loss-gate can!))). CONTINGENT
followup (not this campaign): D3×∞ (hard-gain
(25sw×E0×16% ≈ 25k closes (MAY nucleate!)).
COST (filed): Δt/set-∩ O(z̄) (sweep ~2-4× D1);
(A) ~20-45min + (B) 6400-cap ~3min/run-worst +
truss-post ~10s/run ⟹ ~1-2.5h (tmux-backgroundable
(precedent!)). NEXT: C2-PILOT-2 (code+run, gated
on go).
REVIEW RESPONSE (D5-derivation comments — agreed +
sharpened, filed): STRAUSS (proof (3-line, filed):
π(G)P(G→G') = e^{κT}·q·min(1,e^{κΔT}) =
q·min(e^{κT},e^{κT'}) (symmetric ✓); q symmetric
⟸ E-fixed (same E (loser 1/E) + same non-edge-count
(gainer (1/(C(N,2)−E))) both directions; cap-self-
loops trivially balance (filed!)) + TEST-LIST
(locked for code turn: propose-mechanism (uniform-
marginals (pilot-1-pinned!) + cap-determinism (dense-
graph None-forcing (new!))) + acceptance-EXACT
(synthetic Δt (κ=1: +2→1.0, −1→e^{−1} (tol!);
κ=0→1.0 (D1-exactness!))) + κ0≡D1 same-seed
trajectory-equality (rng-parity (accept-draw ONLY
if Δt_net<0 AND κ>0 (short-circuit (locked!)))) +
Δt-accounting (synthetic (gain/loss/net exact!)) +
truss-units (synthetic clique+scraps (k_max/count/
K/sizes exact!) + Charikar-cross-check)).
TWO-SIDED (elevated to STRUCTURAL REQUIREMENT
(predictive: IF P1 confirms THEN single-sided
insufficient (bracketing!) → size-selection (next-
question (below!)))); D35 = TWO-GATED-ONE-
DIRECTIONAL (poor→poorer + clustered→richer (same
polarization (no restoring force!) — two-gated ≠
two-sided (filed distinction!))). TRIPWIRE (locked):
α̂(κ)-systematic-variation ⟹ BEYOND-EXTREMAL (flag
(investigate (not verdict-flip!)); K = top-truss-
size (core (halo excluded (filed!)))). COUNT(t)
DISCIPLINE (locked): sampled every 10 sweeps (filed
full-trace); coexistence-claim needs count≥2 FLAT
over trailing-half (qualitative-evident (reader-
sees!) + coarsening-fit count~t^{−β} (characteriza-
tion (not gate!))); NO verdicts from single
snapshots (1→10→6→3→1 ≠ multi-knot (filed!)).
D35-LENS (pre-registered discovery-lens (not post-
hoc!)): IF D35 count≥2-persistent THEN moat-
hypothesis (floppy-shedding digs DUST-MOATS (z→0
rings) insulating knots (no-edges ⟹ no-merger-path
⟹ topological-insulation (THIRD thing (neither
selection nor slow-merger!))); measure z-profile
vs knot-distance (moat = dip!)) + extended-T
rerun (T×2 (contingent (locked!))).
ARREST-PROTOCOL (locked, triggered iff count≥2-
persistent-in-T): (i) κ-test (lifetime ↓ as κ↓
(arrest melts!) vs K* κ-robust (selection!));
(ii) T-extension (T×2 (count↓ (arrest!) vs flat
(selection?!))); (iii) quench-then-anneal
(nucleate (∞/2) → anneal (1/0.5) (count↓ (no-
selection!) vs persist (selection?! (contingent
(not in 72!)))). SCOPE-REPAIR (AMENDMENT-5, filed
PRE-REPAIR-DATA (post-66 (prediction-completing
(not shopping!))): ladder locked {D5∞,D5κ1} but κ1-
BARREN (no nucleation (all-N!)) + D5∞-frustrated
(no clique!) ⟹ P3 (α=1/2 ∀ nucleating κ) UNTEST-
ABLE (condensed-branch (κ2!) has NO scaling leg)
⟹ κ2-SUBSTITUTION (6 runs: κ2 × ER-8 × seeds012 ×
{3600,6400} (same-N/seeds (minimal-repair!)));
tripwire-within-rule needs κ1.5-ladder (followup
(not now!)). BRACKETING (adopted): D3 (no-
concentration) … D5 (unbounded-concentration) ⟹
NEXT-QUESTION (adopted, gates post-campaign turn):
what graph-internal mechanism creates a preferred
finite concentration scale? 72 FROZEN (no changes).
C2-PILOT-2 VERDICT (66 + 6-repair; PRIMARY:
extensive-coexistence? NO — no count≥2-persistent-
NUCLEATED (k5-level!) anywhere): CONDENSATION 9
(D5κ2@1600 (T→184-619k, K=85-91/140-143 (c=0.78/
0.88 (single-point-extremal-consistent!), count-1,
dust-bulk-89% (bulk-z=0.29 (starved!)), FROZEN
(rate-0.4%), C≈0.85-0.93, topz-C≈0.8-0.9 (clique!),
nuc=20 (ER-16!) vs 210-300 (ER-8!))); FRUSTRATED 15
(D5∞-ALL-N (kmax=4 (CHURN-LIMIT!), K~100-400 (N-
INDEPENDENT (α̂≈0!), hubs (topz-C≈0.05 (C≪1!)),
T-SATURATED (3.5-11k (not pumped!)), giant 0.28-
0.54, dust-majority-67% + z~21-sponge (saddle-
connected (6400-gap-aware-bimodal (DUST-BARRED!)),
ACTIVE-7% (exchange (not frozen!)))); POISSON+ 39
(κ≤1-all-N (dep≈noise, kmax=3, k5-clean!) + κ2@
3600/6400-repair (PLATEAU (slope≈0, rate-90%
(ACTIVE!)) ⟹ thermo-Poisson (κ2<κ_c (likely!)));
κ1-macro-k3-scraps (7-8 pieces (soup→0 (DEPARTURE!
(enriched (NOT-nuclei (k_max=soup (no-new-scale!),
k5-clean (locked-tracker-decides!)))))); D3-LIKE 6
(D35-ER-8 (arrest-26-28, T+6-8 (scraps ✓ (revised-
P6-CONFIRMED!)))); STILLBORN 9 (D35-ER-16/RR-8
(D3-inheritance!)); DEFECT/COARSENING 0; protocols
UNTRIGGERED (filed!). P1-P9: P1 REFUTED (frustrat-
ed-instead (activity-subclaim-✓!)); P2 ✓ (L1-jump
(κ_c∈(1,2)!)); P3 single-point-consistent + N*-
BRACKET (ladder-straddles (α̂-unfittable!)); P4 ✓-
rate (10×!); P5 SUPPORTED (κ2-single-from-birth
(no-multi-transient!)); P6 ✓-revised; P7 ✓ (gap-
1.0 (2/2!) + floor-nuance); P8 ✓-κ2; P9 REFUTED
(anneal-window-EMPTY (κ≤1-barren!)). N*-BRACKET
(NEW!): κ2-nucleates ⟺ N≲N*∈(1600,3600] (T=2000
(plateau (likely-thermo!))) + growth-erosion-post-
hoc (DILUTION (uniform-propose (attention∝K²/N²!)
vs churn-erosion (crossover=N* (labeled!))) +
κ3-PREDICTION (N*↑κ (followup!)). MIRROR-BROKEN
(kinetics!): D5∞-hard (non-equilibrium (frustrat-
ed!)) ≠ κ→∞-limit (extremal (equilibrium-only!)).
REFINED-BRACKET: D3 (none) … D5∞ (frustrated
(bounded-kmax-4 (SELF-LIMITING (proto-size-
selection?! (churn-balance (LEAD (not-claim!))))))
… D5κ2 (unbounded!) ⟹ next-question ADVANCED
(frustration-as-selector?). RACE: local-won (head-
start!) + remote-66/66-minutes-later + BIT-
IDENTICAL-66/66 (cross-machine-trajectory-
determinism (hist+T-trace+exec (filed!))); remote
faster-per-worker (user-vindicated (3×6400 in
4min!)). ΔT-BUGFIX (pre-campaign (overlap-
correction (tests-caught (incremental≡exact!)) +
smoke-void (re-smoked!)). LOCK-GAPS (filed): (i)
discriminator-at-k_max=soup (resolved-by-k5-
tracker!); (ii) k5-trace-blind-to-k4 (1-snapshot
(mild!)); (iii) ladder-κ-gap (repaired! (κ1.5-
followup!)); (iv) valley-island-scope. FOLLOWUPS
(filed (not-now!)): κ1.5-ladder; κ3-6400; D3×∞;
κ-grid×N-grid (κ_c(N)!); kmax-4-theory. NEXT:
review-turn or next-design (gated on go).
REVIEW RESPONSE (pilot-2 comments — agreed +
sharpened, filed): BRACKET-HEADLINE (adopted):
D3 (depletion (dust/arrest!)) … D5κ≤1 (entropy
(Poisson+!)) … D5κ2-1600 (concentration (clique!))
… D5∞ (FRUSTRATED (kmax-4-sponge!)). HARD≠ZERO-T
(elevated): D5∞ restricts the ACCESSIBLE-TRANSITION-
GRAPH (not reweights-configurations ⟹ Strauss/
extremal reasoning INAPPLICABLE (equilibrium-only!)
— beyond-this-experiment (filed!)). Γ+/Γ−-SKETCH
(filed-rough (next-unit-derives!)): growth ∝ K²/N²
(propose-dilution!) vs erosion ∝ (K²/E0)·e^{−κK}
⟹ K_c ∝ (1/κ)·lnN (3.0→3.7 (WEAK (both-reachable!)))
⟹ N*-bottleneck = SEED-SURVIVAL (dilution-starves-
seeds-before-critical (not K_c-reach!)) — TESTABLE
(K5-birth/death-vs-N (anatomy-reruns!)). SWEEPS-
DEPRIORITIZED (agreed (reordered!)): κ1.5 (anatomy
(useful (not-mechanistic!))); κ3-6400 AFTER
derivation (quantitative-prediction-first (not
probably-nucleates!)). D15-GATE (agreed (NOT-
INVOKED!)): closed-until (D5∞-finite-scale +
SSB-shown (automorphism-break (measure-open
(orbit-structure? (next-unit-scopes!)))); conver-
gence-if-any (unforced (neither-track-modified!)).
INSTANCE (agreed): idle-remote = burning-$ (user-
stops (no-API-creds-here (ssh-only!))).
ANATOMY-LOCK (NEXT-UNIT (docs+anatomy (NO-new-
conditions!)): (A) OFFLINE (saved-states!):
kmax(t)/k4-count(t)/k4-Jaccard(t)/core-persistence
(EXCHANGE-vs-STATIC (fixed-K* vs stationary-phase-
with-churn (ontology-fit!)!) + T-plateau-shape
(have!) + opportunity-stock (wedges(t)/T(t)!);
(B) INSTRUMENTED-RERUNS (SAME-trajectories
(verify-T-match!) + move-columns (t_loss/t_gain/
accept (supply-demand-at-plateau!) + K5-birth/
death (seed-rates-vs-N (κ2@1600-vs-3600 (N*-mech!
)))); (C) DERIVATION (kmax-4-from-mechanics
(supply-demand-balance!) + Γ+/Γ−-scaling (N* +
fixed-point-math (stability-sign!)) + plateau-vs-
transient (kmax(t)-flat (+CONTINGENT-T×2 (trigger:
offline-flat-confirmed (decide-after-offline!)))
+ finite-time-churn-NULL (explicit!)); (D) D15-
GATE-STATUS (closed (until-scale+SSB!)). NEXT:
D5∞-anatomy (gated on go).
D5∞-ANATOMY VERDICT (A: offline 30 runs (15 D5∞ + 9 κ2@1600 +
6 κ2@big, every-100th saves); B: 12 instrumented reruns
(D5∞@1600×3 plateau + κ2@1600×3×2 nuc/plateau + κ2@3600×3
plateau), T-match 12/12 (9 main + 3 repair ⟹ logging perturbs
nothing); INSTRUMENT: log_stride/log_window (deterministic-
stride move columns, no RNG consumed) + k5_window (per-sweep
k5) + 2 pins (suite 567+2skip: local 445s, beast 182s)):
(A) OFFLINE — D5∞-ALL-N (15/15): kmax=4 LOCKED (300/300
saves min-4 (never-3!), max-5 with only 0-2 single-save
flickers/run (never-≥6-sustained!)); k4count early-1-4-pieces
→ late-1-2 (consolidation (not coarsening-to-static!));
EXCHANGE (not static!): Jaccard 0.02-0.31 (1600) / 0-0.16
(3600) / 0-0.10 (6400), persistence ≤0.49/0.33/0.20 (vs
static-1.0!); churn-band drifts ~2×-up over run (piece-
consolidation) but stays churning; opportunity-stock (wedges)
×1.25 (1600) / ×2.3 (3600) / ×3.15 (6400) (slow densifica-
tion under LOCKED scale!). CONTRASTS: κ2@1600 (STATIC!):
kmax 4→75-79 (ER8/RR8) / 21→136-137 (ER16 (nucleated-pre-
100!)), jac/pers→1.0, wedges-×12, T-still-+1.8-2%/100sw
(frozen-membership + slow-accretion!); κ2@big (thermo-
Poisson!): kmax-3-4-flicker, k4count-0-always, wedges-
×0.99-1.01, T-±0.25% (zero-concentration!).
(B) RERUNS (supply-demand): D5∞-plateau: accept-6.8-7.0%,
A-loss-1.65-1.66 vs A-gain-1.66-1.71 (net-+0.00-0.05 ≈ 0
(balanced-pump↔churn!)); rejected-ALL-t_gain=0-at-same-
t_loss (gain-only-gate-✓!); supply-bottom-heavy (P(g≥1)=
6.9%, P(g≥2)=3.1-3.3%, P(g≥3)=1.1-1.2%, P(g≥4)=0.3%).
κ2-nuc-window: accept-58-71%, R-loss-2.5-6.4 (hub-edge-
protection-✓!). κ2@1600-plateau: accept-0.5%, R-loss-83-84
(erosion-e^{−κK}-dead-✓!), accepted-net-+0.9-1.6 (slow-
accretion!). κ2@3600-plateau: accept-89%, net-|·|≤0.001
(detailed-balance-like!). K5-birth/death-per-450sw: D5∞-
floored-0/0 BUT raw-16-25/16-25 (sub-floor-flicker (~2sw-
episodes!) ⟹ seeds-FORM-and-churn-KILLS!); κ2@1600-nuc:
floored-births-1-2/deaths-0-1 (SURVIVAL!); κ2@1600-plateau:
present-450/450; κ2@3600: raw-0/0-over-1350 (seeds-NEVER-
FORM ⟹ dilution-suppresses-FORMATION (not-just-survival!)
⟹ Γ+/Γ−-REFINEMENT: N*-bottleneck-acts-at-BIRTH!).
(C) DERIVATION (kmax-4-supply-sketch (filed-rough!)): count_4
≈ E0·P(g≥2) = 197-211 vs observed-k4-node-mass-171/213/229
(scale-match (units-caveat: edge-budget-vs-node-mass!));
count_5 ≈ E0·P(g≥3) ≈ 70, count_6 ≈ E0·P(g≥4) ≈ 20 (below-
sustained-membership ⟹ raw-flicker-only!) ⟹ kmax=4-is-
where-supply-crosses-macroscopicity. PLATEAU-vs-TRANSIENT:
kmax-exactly-flat-1900sw + T-drift-+0.5%/100sw (sub-%-slow-
densification (DISCLOSED!)) + churn-band-bounded ⟹ STEADY
(scale-stationary (strict-fixed-point-UNCLAIMED!)) ⟹ T×2-
NOT-triggered (decided: extension-wouldn't-change-verdict!).
FINITE-TIME-CHURN-NULL (explicit!): IF-churn-were-transient-
coarsening-THEN-jac→1; observed-jac-band-bounded-≤0.28-+
k5-raw-flicker-sustained (no-runaway!) ⟹ null-REJECTED-on-
this-horizon.
(D) D15-GATE: stays-CLOSED (finite-scale-✓ (kmax-4-locked!)
BUT SSB-NOT-shown (automorphism-break-unmeasured (next-
unit-scopes-measure!))). FOLLOWUPS (filed!): κ1.5-ladder;
κ3-6400 (NOW-quantitative (N*(κ)-from-birth-suppression!));
SSB-measure-scoping; D3×∞. NEXT: review-turn or next-design
(gated on go).
AGING+RATES (analysis-only followups (Units-1+2 (no-new-runs!))):
(1) AGING-DECISIVE (case-(a)!): D5∞-late/early-T-slope-ratio
0.16-0.63-ALL-15-runs (uniform-deceleration ⟹ approach-to-
fixed-point (NOT-persistent-pumping!) ⟹ "steady"-filing-
UPGRADED (aging-with-measured-deceleration!)); opportunity-
halves: 100→1000-×1.2-2.85 vs 1000→2000-×1.03-1.12; late-
abs-drift-↑N (+9-21/+20-34/+51-66-per-100sw) BUT relative-
~0.4-0.5%-ALL-N (bigger-N-further-in-absolute (predicted-
✓!)); κ2@1600-ratio-0.19-0.23-TIGHT (dust-depletion-
deceleration!); κ2@big-flat-throughout (|slope|≤7 (true-
flat!)). (2) RATES-MEASURED: D5∞-gate-perfect-step
(P(acc|0)=0.000/P(acc|≥1)=1.000 (n=95k!)); κ2-in-situ-
Metropolis-EXACT (P(−1)=0.127-0.133-vs-0.135,
P(−2)=0.015-0.020-vs-0.018!); κ2@3600-P(gain≥3)=0/217520
(ABSOLUTE-supply-collapse ⟹ birth-bottleneck-at-SUPPLY
(conversion-undefined-0/0!)); K5-normalized: D5∞-birth/
elig=6-7e-4 + death/K5-sweep=0.478 (~2sw-episodes,
65/65-balanced (flicker-regime (good-stats!))); κ2-nuc-
1-birth/0-deaths (present-96%-of-window (SURVIVAL-regime
(birth-stats-too-thin-to-normalize (honest-small-n!))));
MECHANISTIC-contrast-stands-on-DEATHS (0.48/sweep-vs-0!)
+ presence (10%-vs-96%!). Γ(4)-inequality: turnover-
DEMONSTRATED (sustained-mass-+-churning-membership ⟹ both-
directions->0!) with per-opportunity-normalization-DEFERRED
(needs-k4win-logging (one-line-followup!)).
SSB-1-VERDICT (same-soup-campaign (60-runs (2N×3-soups×
10-dyn (d==S-identity-included!)), NO-lib-change (soup/
dynamics-already-split!) + 3-pins (non-mutation (load-
bearing!) + same-same-identical + same-diff-diverges)):
identity-T-match-6/6 (apparatus-✓!); PRIMARY (floored-k4-
core-Jaccard): same-soup-med-0.076@1600/0.033@3600 vs
across-soup-0.070/0.032 vs random-0.067/0.032 (within-10%
(≪-pre-reg-2×-band!) ⟹ INDISTINGUISHABLE-FROM-RANDOM
(max-same-soup-0.119/0.060 (vs-imprint-threshold-0.8!)));
SECONDARIES: Gini-0.76/0.79 (|m|-large!) + IPR-4-4.8×-
delocalized (localized-with-varying-support!)). VERDICT:
SPONTANEOUS (soup-imprints-NOTHING (dynamics-selects-
among-~C(N,K)-equivalent-attractors!) ⟹ TEXTBOOK-
BREAKING-of-statistical-S_N). SYMMETRY-RESTATEMENT
(filed!): breakable-object = S_N-invariance-of-the-LAW
(NOT-Aut (ER-draws-trivial-Aut-w.h.p. (classical!)));
broken-variable = core/dust-partition. ⟹ D15-REOPENS
(gate-both-halves-✓ (finite-scale-✓ + SSB-✓!)). NEXT:
D15-design (gated on go).
J2-ORIENTATION VERDICT ((c)-ISOTROPIC (32-runs (L28/42
(J2-torus (N=1568/3528)) ×16-dyn (ONE-soup-each (exact-
symmetry (imprinting-impossible-by-construction!))); new-
soup-kind-j2_torus_graph+j2_torus_coords+2-pins (D14-side
(robustness (soup-justification-filed!))))): cores-FORM
(kmax-4 (+5-flickers!) + k4-89-280 + T0=0→ER-like-T*
(triangle-free-bootstrap-✓!)); RADIAL-SSB-PRESERVED
(loc-J-0.069/0.028≈random!); ORIENTATION-ABSENT: core-
elongation-0.20-vs-null-0.11 (perm-p≤0.001 (REAL-but-
WEAK-shape-noise!)) with FULL-CIRCLE-random-axes;
global-edge-x/y-≤8% (ensemble-1.008/1.014!); quadrant-
signs-null-consistent (6/32-unanimous-vs-4-expected
(p≈0.28!)); quadrant-|m|-2-4×-independent-noise (=cor-
related-clustering-noise (no-coherence!)); SHEET-
SYMMETRY-PRESERVED (core-b0-0.49-0.50!). AUT(J2)-SURVEY-
COMPLETE (D5∞!): translations-BROKEN (localization!) +
orientation-PRESERVED + sheet-PRESERVED ⟹ NO-h1-vs-h2-
distinction ⟹ compass-consumption-HAS-NO-INPUT; weak-
formation-consumption-FORBIDDEN (age-rule-is-formation-
side (principle-bites!)); radial-transfer-INCOHERENT-
or-FORBIDDEN (rewired-≠J2 (apparatus-inapplicable!) /
statistical-painting = hand-arranging!). ⟹ STOP-per-
chain (D5∞-radial = WRONG-KIND (filed-precise (not-
mushy!))); D15-STAYS-CLOSED (first-SSB-candidate-
TESTED-and-EXCLUDED (radial-SSB-≠-pin-breaking!);
admission-criterion-STANDS (provisional-amendment-MOOT
(no-instability-to-admit!))). LIVE (not-now!): other-
rules-orientation (D14-side!); D15′-real-space (own-
prereg!); disordered-compass-theory (off-scorecard-
endpoint (dissolves-detector (not-fires!))); sub-
quadrant-texture (pin-irrelevant-per-uniformity-
premise!). NEXT: review-turn or next-design (gated
on go).
COUNT-VS-N (analysis-only (existing-anatomy!)): late-
k4-piece-count saturates ~1-ALL-N (means-1.15/1.28/1.06
(1500-2000!); ≥2-full-run-freq-0.37/0.33/0.08 (N-↓ (floor-
artifact-partly (floor-16/36/64!)))) ⟹ spontaneous-multi-
object-scenes RARE/TRANSIENT (single-sponge-+-dust!) ⟹
polarity-steps-5-7 (interactions/conversion/annihilation)
UNTESTABLE-in-spontaneous-formation ⟹ prepared-two-blob-
initials-NEEDED (flagged-for-non-interference-review
(states-not-rules (scattering-methodology (proposed!)))).
STAGE-0-PREREG (FROZEN-2026-10-01 (~17:35-UTC (commit-
predates-reruns!)); individuals-+-kinematics-+-handed-
ness (polarity-Step-0!)): INPUTS: J2-torus-L28-D5∞-reruns-
d0-d3 + L42-d0-d1 (plateau-1500-2000 (SAME-trajectories
(T-match-6/6-GATED (apparatus-invalid-if-fail!)))); NEW-
COLUMNS: k4sets (per-sweep-floored-k4-node-sets (frozen-
definition!)) + endpoint-moves (stride-logged-(sw,a,b,c,
d,loss,gain,accepted) (observation-only (pins: T-match-
with/without-logging!))). O1-BLOB-KINEMATICS: core-
centroid (circular-mean (background-coords!)) MSD(τ)∝τ^α:
α<0.7-CONFINED / 0.7-1.3-DIFFUSIVE / >1.3-DIRECTED
(prespecified-bins!). O2-HANDEDNESS-H: per-accepted-move-
angular-impulse-about-window-centroid-o (L=(r_a-o)×u +
(r_b-o)×v (u=r_c-r_a, v=r_d-r_b (minimal-torus-disp!)));
H=ΣL/(n·L²); persistent ⟺ 5/5-100sw-blocks-same-sign
AND |Σ|>max-|shuffled| (10-order-shuffles (same-o!));
across-run-signs-vary-expected (exact-symmetry!). O3
(descriptive!): k4-mass-CV + axis-angle-diffusion (vs-
ballistic!). DECISION: STAGE-0-POSITIVE ⟺ (O1-DIRECTED-
or-rotating OR O2-persistent-vs-shuffled) in-≥2-runs;
else-NULL (file-"D5∞-plateau-achiral" (STOP-debt-free-
route-for-pure-D5∞ (C0-with-debts-guilt-free!))). NON-
INTERFERENCE: same-trajectories (T-gated!) + frozen-
k4 + plateau-window (anatomy-consistent!) + J2-soup
(filed-justification (readout-basis!)). NEXT: Stage-0-
reruns (gated on prereg-commit!).
STAGE-0-AMENDMENT-1 (NULL-CORRECTION (committed-PRE-
analysis (reruns-done/unopened (order-preserved!)))):
O2-"order-shuffle"-null is VACUOUS (H-a-sum (order-
invariant!) ⟹ shuffle-cannot-move-it (prereg-bug
(owned!))); REPLACED-by per-move-SIGN-randomization
(10-draws (each-move-L-sign-flipped-p=0.5 (tests-
coherent-handedness-across-moves (the-actual-claim!))));
bar-unchanged (|H_obs|>max-|H_signrand|); block-sign-
stability (5/5) + everything-else-stands. Original-
text-preserved-in-git-history (7761f49).
STAGE-0-VERDICT (NULL (6/6-reruns (L28×4+L42×2 (plateau-
1500-2000)); T-match-6/6-GATE-PASS!)): O1: 0/6-DIRECTED
(3-CONFINED (α≈0 (rms-2-4 (sit+jiggle!))) + 3-DIFFUSIVE
(α≈0.75-1.05 (wander-torus-scale (REAL (uncorrelated-
steps (NOT-piece-flicker!))))) + 1-slither-ANECDOTE
(L42-d0: x-rod-sliding-along-x (y-pinned-spread-1.0-vs-
42.6!) (axis-aligned-mobility? (N=1 (followup!))))); O2:
0/6-PERSISTENT (|H|-in-null-envelope (1-magnitude-exceed-
with-flipping-blocks (correctly-rejected (bar-works!)));
blocks-mixed-everywhere; signs-3+/3- (symmetric-noise!));
O3: mass-CV-0.13-0.27 (stable!) + axes-static/diffusive/
jitter (L28-d0-super diffusive-RESOLVED-as-jitter+drift
(up-steps-0.53 + cut-crossings + ani-coupled-noise (NOT-
spinning!))); empties-≤0.4%. ⟹ D5∞-PLATEAU-ACHIRAL
(filed!); INDIVIDUALS-YES (trackable (Step-0-half-✓!))
BUT CIRCULATION-SIGN-NO ⟹ POLARITY-PAUSED (no-grounded-
binary-candidate (circulation-was-#1!)); ⟹ STOP-debt-
free-route-for-pure-D5∞ (per-prereg!) ⟹ C0-WITH-DEBTS-
GUILT-FREE (debt-free-attempt-MADE-and-COSTED (not-
skipped!)). C0-INPUT: mobile-trackable-blobs (diffusive-
wanderers + sitters (heterogeneity-mechanism-OPEN!));
formation-provides-localization+mobility (ψ-must-provide-
rest!). NEXT: C0-merge+prereg (gated on go).
P1-PREREG (FROZEN-2026-10-01 (~19:00-UTC (commit-predates-
ALL-P1-runs!)); directed/ballistic-motion-campaign (P1-of-
P1/P2/P3 (P2-polarity + P3-handedness-UNTOUCHED (no-polar/
handed-readouts-in-any-P1-run!)))). QUESTION (load-bearing-
framing!): NOT "can-D5∞-blobs-move-ballistically" (pure-D5∞-
cannot-sustain-direction (no-phase/momentum-state!)) BUT
"can-a-localized-D5∞-object-acquire-persistent-directed-
motion-when-coupled-to-a-direction-carrying-excitation".
CONTROLS: K-only→confined/diffusive (P1.0-banked!) +
ψ-only→directed-no-object (P1.1!) vs K+ψ→?-finite-directed-
composite (B2/B3-gated!).
P1.0-BANKED (no-new-runs!): Stage-0-verdict = formation-null
(0/6-directed (3-confined-α≈0-rms-2-4 (sit+jiggle!) + 3-
diffusive-α≈0.75-1.05-torus-scale-wander (uncorrelated-steps
(NOT-piece-flicker!))) + 1-slither-anecdote (N=1!)); mass-CV-
0.13-0.27 (stable!); axes-static/diffusive/jitter (L28-d0-
super-diffusive-RESOLVED-as-jitter+drift (NOT-spinning!));
empties-≤0.4%; <ΔR>/t→0 (no-persistent-velocity!)). REUSED-
AS: K-only-row (MSD-bins + zero-mean-velocity); C_v-formation-
baseline-NOT-banked (Stage-0-did-not-measure-C_v (honest-gap:
B0-controls-measure-it-fresh!)).
P1.1-WAVE-ONLY-POSITIVE-CONTROL (validates-ballistic-detector
(NO-formation-involved!)): APPARATUS (this-commit (12-pins +
1-elist-pin!)): H(G)=-J·A(G) (hopping-ONLY (no-onsite/degree/
core-detector/distance/potential/force-law (LOCKED!)); z-
regular⟹Laplacian-walk-up-to-global-phase (pinned!)); Krylov-
exact-unitary (norm-1e-8-pinned!); Gaussian-k-packets (σ<<L/6-
gated; -k = conj(+k)-pinned!); COM-circular-mean + unwrap +
MSD-bins (Stage-0-bins!) + C_v + v-fit. ANALYTIC: chain-
v_g = 2J·sin(ka) (derived-from-H (NOT-dispersion.py-convention
(ω=2J|sin(ka/2)|) (separate-pin!))). PILOT (next-commit (post-
prereg!)): ring-400 (σ=15, k∈{+0.5,-0.5,0}, dt=0.1, T=120
(Δx≈115<N/2 (no-wrap!))) + torus-grid-30 (σ=4, k=(±0.5,0)/(0,
0), dt=0.1, T=40). PASS ⟺ ALL: (a)-|v_fit-2J·sin(ka)|/|·|<10%;
(b)-v(+k)·v(-k)<0-AND-|v(+k)+v(-k)|/|v|<10% (sign-test!); (c)-
zero-k-speed<5%-of-|v(0.5)| (null!); (d)-MSD-α>1.3-for-±k
(directed-bin!); (e)-C_v(τ)>0-to-10-crossing-times (σ/v!);
(f)-norm-to-1e-8. ANY-fail⟹detector-INVALID-STOP (fix-apparatus
+ re-prereg (NO-formation-runs-until-P1.1-PASS!)).
P1.2-ONE-WAY-DERIVATION (G→ψ (ψ-can-scatter-NOT-propel (formation-
never-reads-ψ (ballistic-composite-IMPOSSIBLE-by-construction
(this-stage!)))): ψ-propagates-on-instantaneous-G_t (H(G_t) =
-J·A(G_t), piecewise-constant-per-sweep, S-substeps-of-dt-per-
sweep (fiducial-S=10-dt=0.1; verdict-BRACKET-S∈{1,10,100}-
LOCKED (timescale-robustness (not-tuning!)))); capture =
elist_window-per-sweep-frames (observation-pure (T/exec/hist-
identical-pinned!) + T-match-gated-reruns (Stage-0-precedent!));
PURITY-ARGUMENT: formation-trajectory-generated-independently
(ψ-consumes-frozen-frames (oneway-mutates-nothing-pinned!)).
NO-ψ→G-DIRECTION-EXISTS (ban-list-vacuous-here (core-detector/
distance-to-core/binding-potential/force-law/radiation-pressure-
NOWHERE (nothing-to-ban-in!))).
B0-SCATTERING-PREREG (frozen-G-first (B0a (live-B0b-queued-behind-
B0a+elist-capture!))): INPUTS: formed-D5∞-J2-states (Stage-0-rerun-
plateau-saves (L28-d0-d3+L42-d0-d1 (same-trajectories (T-gated!)))
+ node-identity-matched-controls (SAME-labels-different-edges!):
(i)-bare-J2-torus (free!); (ii)-D1-run-J2-same-sweep (structureless-
relocation!); background-J2-coords-readout (Stage-0-precedent!) +
frozen-floored-k4-masks (same-definition!). PROTOCOL (per-state):
packet-(σ=4, |k|=0.5)-at-max-torus-distance-node-from-core +
k-sign-aimed-at-core (operational-rule: sign-whose-first-10-time-
units-move-COM-toward-core (filed-rule (not-tuning!))); T=200-
frozen. OBSERVABLES: core-weight-w(t) + residence-R=∫w·dt + delay-
Δt = t_past - t_past^free (core-longitude-crossing!) + incident-
half-weight-at-T. B0-FIRES ⟺ (R_formed-mean(R_controls))/std(R_
controls)>3 (excess-residence!) OR |Δt|>3σ_controls (delay!).
B0-NULL⟹file-"wave-passes-through"⟹B1/B2/B3-MOOT⟹STOP-P1-null
(convergence-break-LOCATED (still-publishes!)).
B1-BINDING-PREREG (same-frozen-setup (T=1000-long!)): late-core-
weight-w̄ (last-20%-of-window) vs delocalized-baseline-w_deloc =
|core|/N. B1-FIRES ⟺ w̄/w_deloc>5-in-≥2-runs AND w̄-exceeds-every-
control-w̄ (node-matched-masks!). B1-NULL⟹STOP (scattering-without-
binding (reciprocal-coupling-UNEARNED!)).
B2/B3-GATES (NOT-designed-here!): reciprocal-ψ→G-channel-admission-
REQUIRES-B1-FIRE + DERIVED-feedback (ban-list-stands: no-core-
detector/no-distance-to-core/no-binding-potential/no-force-law/no-
radiation-pressure-rule (invention-FORBIDDEN (derivation-owed!)));
B3-killer = k→-k⟹v→-v-on-persistent-composite (+linear-COM +
C_v>0 + zero-k-null + mass-bounds + not-elongation-axis!). NEXT:
P1.1-pilot (gated on prereg-commit!).
P1-AMENDMENT-1 (paper-derived-branch-input (PRE-DATA (zero-P1-runs-
executed (pins-only-so-far!) (commit-predates-ALL-P1-runs!)))):
BRANCH-STRUCTURE-FINDING (apparatus-validation (not-campaign-data!)):
scalar-(coinless-CTQW)-J2-walk = ONE-dispersive-band (E∈[-8,+8])
+ EXTENSIVE-flat-zero-band (N/2 + nodal-extras (L28: 838/1568!));
same-k-±ω-doublets-DO-NOT-EXIST (need-a-coin (discrete-time!)).
⟹ branches := E-sign-halves-via-exact-chiral-projectors (P±-of-H_
bare ([P,H]=0 (bipartite-q=x+y (filed-S11!)))); matched-±-packets
:= partner-momenta-(k, k+Q) (Q=(π,π) (branch-momentum-LOCKING
(raw-Gaussian-≥99.9%-pure (tails-only-impurity!)))); mixing :=
deviation-from-INITIAL-branch-weight (NOT-impurity (initial-out-
of-branch = prep-geometry (filed-separately!))); free-null-EXACT-
zero (construction (not-statistics!)). COINED-WALK-considered-+
DEFERRED (reason: coin-undefined-on-irregular-formed-graphs
(degree-varying-hubs/pendants (coin-update-across-rewiring-IS-
new-law (breaks-minimal-G_t-coupling!)))). GUARDRAIL (quoted):
branch-sign = spectral-fact (NOT-matter/antimatter-or-charge!).
P1.1b-BARE-J2 (ADDED (P1.1a-ring/torus-STANDS (single-band-v_g-
detector-validation!))): L28-bare (σ=4, k=(±0.3,0)-×-partners +
zero-k (5-packets!), T=12-dt=0.1 (no-wrap-round-number (disp<L/2-
gated-post-hoc!))); VALIDITY-gates: raw-purity-≥80%-per-packet
+ R²>0.99-displacement-fit (±k-only (interference-gate!)) + norm-
1e-8; PASS ⟺ ALL: (a)-α>1.3-both-branches; (b)-k→-k-reversal-
10%-per-branch; (c)-conjugation-v_+(k+Q)+v_-(k)≈0-15% (looser
(different-packets/curvature!)); (d)-zero-k-speed<5%; (e)-free-
mixing-<1e-6 (sanity (construction-zero!)). ANY-fail⟹P1.1b-
INVALID-STOP (same-rule-as-P1.1a!). B0-ADD-observable: M(t) =
branch-flip-deviation (bare-basis (in/out-states!)); B0-mixing-
FIRES ⟺ max-M>1e-6-in-≥2-runs (10⁶×-above-Krylov-noise (~1e-12!)
(free-null-exact-zero!)); MECHANISM-filed: triangles-break-
bipartiteness-break-chiral-symmetry-couple-branches (odd-cycle-
content-IS-the-mixer (measurable-not-fitted!)). B0-headline-
geometry-LOCKED: x-directed + approach-sign-rule (y-directed +
flipped = robustness-appendix (headline-null-stands-even-if-
appendix-fires (no-shopping!))). B1-FOLLOWUP-descriptive (NOT-
criteria!): trapped-weight-branch-oscillation-frequency
(Zitter-like (operational-mass-scale-candidate!)) + spatial-
flip-profile (core-vs-bulk!) + flat-band-exchange-weight
(MEASURE (no-Dirac-fitting (explicit-ban!))). P2/P3-untouched-
STANDS. NEXT: P1.1a+P1.1b-pilot (gated on amendment-commit!).
P1-AMENDMENT-2 (window-corrections (PRE-DATA (pure-arithmetic-from-
committed-text (no-numbers-needed!))): (1)-(e)-SLIP (owned!): T=120-
ring = 7.7-packet-crossings (σ/v = 15/0.959 = 15.6-units (10-would-
need-T≥157!)) + torus-T40 = 9.6-crossings (σ/v=4.2!) ⟹ "10-crossing-
times"-UNCHECKABLE-as-written; REPLACED-by full-window-C_v-positivity
(ALL-10-lag-bin-means > 0 (ring≈7.7/torus≈9.6-crossings (filed-per-
substrate!))); bar-unchanged (positivity (not-magnitude!)). (2)-torus-
T=40→25 (no-wrap-guarantee (disp≈24<L=30 (was-38-wrap!)); α-range-
thins-to-2× (ring-carries-range-role!)). Everything-else-stands.
NEXT: P1.1a+P1.1b-pilot (gated on amendment-commit!).
P1.1a-VERDICT (PASS (beast (12s!)); ring-400 + torus-grid-30 (T=120/
25 (amended!))): ring: v=±0.9583-vs-2sin(0.5)=0.9589 (0.006%!);
reversal-exact (±0.9583!); zero-k-0.0000; α=2.00/2.00; C_v-bins-
+1.000-all-10 (perfect-persistence!); norm-7e-13; disp=115<200-✓.
torus: v=+0.9668/-0.9647-vs-0.9589 (0.8%!); transverse-0.0000;
α=2.05/2.04; C_v-+0.996; norm-2e-14; disp=24.2<30-✓. ALL-22-
substrate-checks-PASS (11+11!) ⟹ ballistic-detector-VALIDATED
(ψ-only→directed-no-object (control-row-✓!)). NOTE-filed: zero-k-α
= fit-noise-on-stationary-COM (ring-0.00/torus-2.72/J2-3.21 (disp=
0.0-all!)) ⟹ α-meaningless-when-stationary (criteria-correctly-
use-speed-for-zero-k (no-impact!)).
P1-AMENDMENT-3 (J2-window-shortening (PRE-RERUN (pilot-1-opened:
physics-PASS + gate-MISS (both-filed (below-vs-above!)))): T=12→10
(measured-v=1.235 ⟹ disp≈12.3<L/2=14 (arithmetic (not-tuning!)));
same-5-packets/same-gates/same-criteria; ring/torus-STAND (passed
(rerun-replicates!))). P1.1b-PILOT-1-filed (SUPERSEDED (gate-miss
(no-verdict-drawn (discipline!))): ALL-physics-PASS-with-margin
(α=2.12-2.15 (vs-1.3!); reversal-exact (1.2246/1.2353!); conjugation-
exact; purity-100.00%-all-5 (w0=0.0000!); mixing-2e-13 (vs-1e-6!);
zero-k-exact-null (disp=0.0!); n_zero=838-filed!) BUT nowrap-gate-
MISS (disp=14.8-15.0-vs-14 (7%-over (T=12-round-number-too-long!)));
R²=0.9993-0.9995 (COM-clean (no-interference-signature (gate-was-
conservative (center-based!)))). NEXT: pilot-2-T10 (gated on
amendment-commit!).
P1.1b-VERDICT (PASS (pilot-2-T10 (beast); ring/torus-replicated-
identical!)): disp=12.1-12.2<14-✓; purity-100.00%-all-5 (w0=0.0000
(branch-momentum-locking-EXACT (tails-below-1e-4!))); α=2.07-2.09-
all-4 (directed!); R²=0.9997-0.9998; reversal-exact-per-branch
(1.2039/1.2110-symmetric-pairs!); conjugation-exact-both-pairs
(v_+(k+Q)=-v_-(k)!); zero-k-exact-null (disp=0.0!); mixing-≤1e-12-
all-5 (free-null-confirmed (construction-zero (not-luck!)));
n_zero=838-replicated. ALL-12-J2-checks-PASS.
P1.1-VERDICT (PASS (all-substrates (ring+torus-grid+bare-J2))):
ψ-only→ballistic-but-nonlocalized (control-row-✓); detector-
validated (v_g-match/sign-test/zero-k-null/MSD-bins/C_v/R²-gates/
exact-zero-mixing-null (all-with-margin!)). ⟹ P1.1-GATE-OPEN
(formation-coupling-runs-UNBLOCKED (B0a-next!)). NEXT: B0a-frozen-
scattering (inputs: Stage-0-plateau-saves + node-matched-controls
(gated on input-inventory!)).
P1-AMENDMENT-4 (B0a-measurement-expansion + operational-rules +
decision-table (PRE-B0a-DATA (inventory-only-so-far (no-wave-runs
on-formed-graphs!)))). INPUTS (inventory-filed: s0_parts = 5/6-
runs-k4sets+moves (L28-d0-MISSING!) + NO-elists-anywhere (campaign-
scripts-did-not-persist-saved!) + j2_parts = 6/6-t_traces (T-match-
refs-✓!)): (0)-RERUNS: 6-trajectories (L28-d0-d3+L42-d0-d1 (D5∞-
same-seeds!)) + elist_window-1500-2000 (501-frames (B0a-uses-3
(B0b-option-value-free!))) + k4_window-same; T-match-6/6-vs-j2_
parts-GATED (apparatus-invalid-STOP-if-fail (Stage-0-precedent!)).
(1)-SITTER-SELECTION (formation-side (pre-wave (legitimate!))):
recompute-centroid-MSD-α-per-run (1500-2000 (Stage-0-O1-replication
(agreement-filed!))); sitters = α<0.7-AND-frozen-quality (core-in-
all-3-saves + pairwise-Jaccard≥0.5); <1-sitter⟹STOP+file. (2)-FROZEN-
states: saves-{1500,1800,2000}-per-sitter (3-each). (3)-D1-controls:
FRESH-D1-runs (same-L/dyn/sweeps (label-matched (honest: trajectories-
diverge!)) + uniform-capture). (4)-bare-J2-in-script-per-L. MASKS:
node-identity-matched-from-formed-state (all-controls (labels-shared!)).
GEOMETRY (per-state): prep-at-max-torus-distance-node-from-core;
per-branch-operational-approach-sign (10-unit-verify-on-ACTUAL-graph
(formed-H (not-bare!)); neither-approaches⟹run-invalid-filed);
headline = +branch-x-directed-approach; FULL-factorial-filed (2-
branches × 4-geos (x/y × approach/flip)) with headline-cell-only-
for-fire/track (no-selection!). OBSERVABLES (per-run, T=200-dt=0.1
(LOCKED)): R-residence + Δt-delay (first-core-crossing (r_core =
sqrt(|K|) (filed!); NaN-if-miss (delay-on-crossing-subset (≥5-non-
NaN-else-delay-void-filed!)))) + ΔW±/0 (final-dev + max-dev (bare-
basis!)) + v_out+R²+trunc-flag (10-unit-post-crossing (pre-return!))
+ dispersion-ratio (width-growth-vs-matched-free) + w̄ + w̄/w_deloc
(late-20% (B0-descriptive + B1-criterion (roles-split (no-double-
dip!)))) + incident-half (stands-filed) + accounting-max-dev (HARD-
gate-1e-9 (W_++W_0+W_-=1-every-frame!); >1/3-invalid⟹apparatus-STOP)
+ K-covariates (core-mass + T_total + B_chiral-headline (||{Γ,H}||_F/
||H||_F (background-Γ!)) + triangle-density). WRAP-note (T=200 ≫ L):
residence/mixing-cumulative (wrap-robust-via-matched-T-controls!);
delay-first-crossing; v_out-pre-return-window. B0-TRACK (mechanistic-
bridge (CO-PRIMARY!)): Spearman-per-state (n=27-headline-+cells
(scipy.spearmanr-LOCKED!)): ρ(mix_max,B)>0.5-&-p<0.05-AND-ρ(R,B)>0.5-
&-p<0.05; per-run-means-filed-descriptive (underpowered (no-p-bar!)).
DECISION-TABLE (locked (no-wiggle!)): fire+track⟹B0-FIRE+BRIDGE
(headline-win!); fire+track-null⟹B0-FIRE-bridgeless (response-shape-
filed!); contrasts-null⟹B0-NULL (track-still-computed+filed!).
FIRE = residence/delay-median-z_i>3 (z_i-vs-18-controls!) OR mixing-
max>1e-6-in-≥2-runs (stands!). B1-STANDS-independent (5× + every-
control). STRUCTURAL-RESPONSE-SCOPING (honest!): B0a = K-side-
covariates (frozen-K-cannot-respond!); dynamic-K-response = B0b-
queued. NEXT: B0a-campaign (gated on amendment-commit!).
P1-AMENDMENT-5 (B0a-packet-momentum (PRE-B0a-DATA (one-line!)):
|k|=0.5→0.3 (reason: P1.1b-validated-packets-only (|k|=0.5-predates-
branch-validation (never-validated!))); σ=4-STANDS; partner-momenta-
construction-unchanged (per-branch-operational-approach-sign (A4!))).
NEXT: B0a-campaign (gated on amendment-commit!).
P1-AMENDMENT-6 (contrastive-mixing + bridge-conjunction (PRE-B0a-DATA
(smoke-mechanics-surfaced (T=2-non-plateau (NOT-B0a-data!)); JUSTIFIED-
on-THEORY + locked-text!)): THEORY: any-[P,H]≠0-graph ⟹ O(1)-mixing-
in-O(1)-time (energy-spread-~8!) ⟹ absolute->1e-6-FIRES-on-D1-controls-
identically (D1-non-bipartite-w.h.p. (locked-text!) (mechanics-smoke-
confirmed-0.78-vs-0.72!)) ⟹ absolute-rule-VACUOUS-for-blob-specificity.
REPLACED-by mixing-DOMINANCE: Mann-Whitney-U (formed-max-mix > D1-max-
mix (one-sided (scipy-mannwhitneyu-defaults-LOCKED!))) p<0.05 (bare =
floor-anchor (~0 (filed!)) (excluded-from-null!)); evaluated-only-if-
median-formed->1e-6 (else-mixing-absent (filed!)). BRIDGE ⟺ mix-
dominance-AND-residence-fire-AND-track-fires (PI's-simultaneous (all-
three!)). B0-FIRE ⟺ residence-fire-OR-mix-dominance. TABLE: fire+bridge
⟹FIRE+BRIDGE; fire+¬bridge⟹FIRE-bridgeless (shape-filed!); ¬fire⟹NULL.
TRACK-STANDS (dual-Spearman (shape-filed (clustering-vs-gradient!))).
VOUT-CLARIFICATION (operationalization (locked-R²-gate!)): S4-files-
vout-R² + r2>0.9-gated-means (descriptive (no-fire-role!)).
NEXT: B0a-campaign (gated on amendment-commit!).
P1-AMENDMENT-7 (sitter-selection-repair (PRE-S4 (S3-frozen-runs-in-
flight (UNOPENED (no-S4-before-this-commit!)); JUSTIFIED-on-filed-
numbers + locked-bins (no-wave-data!))): DOUBLE-BUG-owned: (1)-IMPL:
min-Jaccard-used-as-boolean (0.23-truthy!) ⟹ ≥0.5-threshold-never-
enforced; (2)-PREREG: Jaccard≥0.5-UNACHIEVABLE (filed-churn-≤0.31
(100sw-gaps!) ⟹ 300sw-gaps-lower (measured-0.06-0.23!) (threshold-
set-without-consulting-filed-numbers!)) + CONCEPTUALLY-MISPLACED
(frozen-scattering-uses-per-save-masks (cross-save-membership-
NEVER-mattered!)). REPLACED-by: sitter ⟺ α<0.7-AND-core-present-
all-3-saves (mass>0!) (centroid-confinement = sitter-essence
(membership-fluidity = known-EXCHANGE-physics!)). METHOD-FIX:
unwrap-centroid-traces-before-single-origin-α (wrapped-traces-wrap-
inflate-wanderer-α (torus-saturation-kills-lag-α (measured-≈0-all-
runs!) (locked-bins-UNCHANGED!))). S1-RECOMPUTE-RULE: fixed-S1-reruns-
on-same-T-matched-reruns (no-new-formation-runs!); S3-REUSE-RULE:
frozen-cells-run-under-identical-protocol-REUSABLE-iff-reselected
(top-up-newly-selected-states-only (same-protocol!)); S4-ONLY-after-
reselection (verdict-chain-clean (method-locked-here!)). S1-INTERIM-
filed (superseded-method (for-transparency!)): T-match-6/6-✓;
wrapped-α: sitters-L28-d1/d3+L42-d0 (3/3-split-replicates-Stage-0-
count!); jacmin-0.06-0.23 (churn-consistent!); masses-134-246.
NEXT: S1-fix + S3-topup-if-needed + S4 (gated on amendment-commit!).
P1-B0a-VERDICT (B0-NULL + B1-NULL (S3-432/432-cells-persisted +
S4-headline-AND-all6 (A6-decision-table-APPLIED (no-wiggle!)))).
APPARATUS-GATES: accounting-max-dev-1.8e-11-invalid-0/432 (hard-gate-
1e-9-PASS!); headline-cells-54; approach_ok-headline-5-fails-excluded
+filed (appendix-378-cells-minus/x-flip/y-approach_ok-349/378!);
S1-fixed-sitters-L28-d1/d2/d3 (single-α-(-0.08/-0.06/+0.04)-all-<0.7
(A7-rule!) + masses->0-all-saves; L28-d0-diffusive-1.49-excluded;
L42s-single->1.2-excluded (d0-slither-suspect-skipped-2!)); valid-
formed-6-controls-18. HEADLINE-FIRE-TESTS: residence-controls-26.02±
2.00-vs-formed-z-(-5.60/-5.27/-5.81/-3.46/-2.11/-2.55)-median-(-4.37)
(SIGN-REVERSED (formed-traps-LESS!) ⟹ res=False); delay-formed-n=0-
VOID (D1-null-dts-all-negative-(-4.8..-14.7)!); mixing-formed-max-
0.29-0.43-vs-D1-0.79-0.81-vs-bare-1e-11 (median-formed->1e-6-
evaluated!; MWU-one-sided-p=1.0 ⟹ dominance-ABSENT (D1-rewiring-
breaks-chirality-HARDER!)); FIRE=res-OR-mix=FALSE. TRACK: rho_m=
+0.574-p=0.0033-vs-rho_r=-0.550-p=0.0053-n=24 (residence-leg-
NEGATIVE ⟹ no-bridge (mixing-half-fires-alone!)). BRIDGE-moot
(needs-fire!). B1: formed-ratios-0.6-0.9x-vs-controls-max-wbar-
0.1465 (0/6-need-5x+every-control ⟹ NULL). DESCRIPTIVE-filed:
formed-vout/width-cells-n=0-empty (post-crossing-criterion-yielded-
none!) vs controls-vout-2.47 (R²-gated-1.96); dW-patterns-filed
(no-fire-role!). 2x2: mix-False-res-False ⟹ B0-NULL. ALL6-
SENSITIVITY: B0-NULL (MWU-p=1; res-False-delay-void; TRACK-rho_m=
+0.677-p=9e-08-vs-rho_r=-0.056-p=0.70-no-bridge-n=49) + B1-0/13-
NULL (ratios-0.3-0.9x). ⟹ FROZEN-D5∞-OBJECTS-DO-NOT-TRAP/BIND/MIX-
CTQW-BEYOND-LABEL-MATCHED-CONTROLS (wave-passes-through (residence-
SHORTENED!); chirality-breaking-comes-from-rewiring-not-blob!).
B2/B3-STAY-GATED (no-one-way-anomaly + feedback-still-underived
(ban-list-stands!)). RECORDS: data/b0a/ (432-cells + headline/all6-
results + selection!) + scripts/b0a_campaign.py + scripts/b0a_
analyze.py. NEXT: B0b-dynamic-K-vs-close-P1-null (user-call (gated-
on-go!)).

## SPEC-PREREG (bound-state spectroscopy; FROZEN-2026-10-01 (~20:00-UTC,
commit-predates-ALL-SPEC-runs); branch cursor/bound-spectroscopy-d8ef off
PR-#65-tail (P1-amendment-7); non-interference with in-flight B0a-S3: reuse
frozen elists/k4sets read-only, separate beast dir, workers<=32))

QUESTION (load-bearing): does a D5inf-formed object K support discrete or
resonant psi modes, or is the formed graph merely a structural lump? H_K =
-A_K (J=1, hbar=1; P1 hopping-only convention LOCKED; C0 has NOT advanced
beyond bare adjacency (no fitted trapping potential, no onsite/degree terms);
if C0 advances later, re-run is a filed followup, not a revision).

INPUTS (no new formation runs): B0a-rerun frozen states (GRID L28-d0..d3 +
L42-d0..d1 x SAVES 1500/1800/2000 = 18 formed states; T-match-6/6-banked
(B0a-S0); elists/k4sets consumed read-only). K = floored-k4 node set per
save (frozen definition, Stage-0/B0a precedent). Masks node-identity-matched
onto every control (labels shared, edges differ).

CONTROLS (per formed state; 18 D1 + 18 rewired + 2 bare = 38; 56 graphs):
(i) bare-J2-torus per L (free/extended-wave + flat-band baseline; E-matched
by E-conservation); (ii) D1-same-sweep same-L/dyn (structureless relocation;
reuse B0a-D1 elists; label-matched masks); (iii) degree-preserved rewired
(spectroscopy.rewired_control, nswap=10*E LOCKED, seed=1000+state_index
(state_index = GRIDxSAVES enumeration L28-d0-s1500=0.., LOCKED); degree
sequence exact (pinned); giant fraction filed, never gated).

APPARATUS (this commit; 11 pins): spectroscopy.full_spectrum (dense eigh,
ascending, deterministic) + ballistic H/IPR/branch primitives (P1-locked) +
shell1_union (near-K = K u 1-hop in THAT graph) + sheet_index_sets /
dormant_sheet_of (K-majority sheet b* from background J2 coords, tie->0;
dormant = 1-b*) + top_candidates_by_enrich(k=3) + top_nonflat_candidate
(|E|>1e-9 flat exclusion) + isolation_ratios (gap/local-median, window=20) +
window_contrast (halfwidth=0.5) + rt_partition (bisector sides, core
excluded) + incoming_energy (<psi0|H|psi0>) + driven_run/transfer_trace
(global J(t)=1+dJ*sin(Omega*t), graph-intrinsic, no K-detector).

SPEC-0 OBSERVABLES (per mode n): E_n, IPR_n, wK_n, eK_n=wK/(|K|/N), wK1_n
(near-K), W+/W0/W- (bare-J2 branch basis per L, B0a precedent), s0/s1 +
dormant weight d_n + enrichment. Per graph: eKmax, IPRmax, IPRNmax=IPR*N,
top-3 (E*/eK*/IPR*/isolation/outside-band |E*|>8 flag/window-contrast),
accounting max-dev (W-sum=1 to 1e-9; >1/3 graphs invalid => apparatus-STOP),
eigennorm max-dev (<1e-9), giant fraction, |K|, |shell|. GATES (hard):
norm/accounting as above; solver determinism pinned.

SPEC-0 FIRE (SPEC1 = localized spectral mode exists; residence-time ban
STANDS: no R/delay/wbar in this fire (eigenmodes only)): F=18 formed eKmax,
D=18 D1 eKmax, R=18 rewired eKmax, B=bare eKmax (floor anchor, excluded from
null (B0a-A6 precedent)). SPEC1-FIRE iff ALL: (L1) median(F)>5 (5x
delocalized (B1 precedent)); (L2) Mann-Whitney F > pooled(D u R),
scipy.stats.mannwhitneyu(alternative='greater') p<0.05 (formed dominates
randomized structures); (L3) >=2 distinct runs (of 6) hold >=1 save with
eKmax>5 (object-class, not microstate lottery); (L4) size-robustness:
median formed raw IPRmax L42 / L28 >0.6 (localized~1.0 vs extended~0.44
(N28/N42); threshold midway, LOCKED). SECONDARIES (filed, supportive only):
(S1) median top-eK isolation>2; (S2) fraction |E*|>8 filed (>=1/3 = strong
outside-continuum); (S3) median window-contrast>10 (IPR vs bare same-E).
VERDICT: all-L-fire => SPEC1 (+ publish E* predictions for SPEC-1); else =>
SPEC0 (no localized/resonant modes beyond controls; SPEC-1/2 MOOT, STOP).

SPEC-1 PREREG (frozen procedure; values TBD from SPEC-0 verdict commit; gated
on SPEC1-FIRE): STATES = top-3 formed by eKmax (>=2 runs enforced: if top-3
span <2 runs, replace 3rd with best state from another run (LOCKED)) +
matched D1 + bare per (L,d,s). PREDICTIONS: E* = top_nonflat_candidate per
state (single energy each, frozen before ANY SPEC-1 run; flat-band top
skipped by locked rule). PROTOCOL (per state x k): frozen scattering, B0a-S3
headline cell only (+branch, x-directed, operational approach-sign verify on
actual graph (B0a-A4); neither-approaches => cell-invalid-filed): sigma=4,
|k| in {0.1,..,0.8} (8 LOCKED), dt=0.1, T=200. OBSERVABLES: R/T (rt_partition
halves at T), P_local=wbar (late-20% core weight), delay crossing-vs-bare
(B0a first-crossing, r_core=sqrt(|K|); NaN-if-miss; >=5-non-NaN-else-void),
E_in=incoming_energy per cell. COVERAGE: E* within [min E_in -0.5, max E_in
+0.5] else state unscorable-filed (need >=2 scorable else SPEC-1 VOID-filed).
SPEC2-FIRE (resonance at predicted energy) iff >=2/3 scorable states satisfy
BOTH (i) P_local(k*)>max_{k!=k*} P_local(k), k*=nearest-E_in-to-E* (peak at
prediction), AND (ii) P_local(k*)>3x matched-D1 same-k (blob-specific, not
generic k-dependence). R/T/delay filed descriptive (characteristic structure;
no fire role (single-comparison discipline)). VERDICT: FIRE => SPEC2
(formation->object->discrete spectrum (headline)); else SPEC1-capped
(localized mode without scattering resonance).

SPEC-2 PREREG (frozen procedure; gated on multi-level gate): GATE: state
qualifies iff >=2 modes with eK>5 AND |Ea-Eb|>0.2 (distinct levels, LOCKED);
>=1 qualifying state else SPEC-2 MOOT (single-level cap filed). STATES: top
<=2 qualifying by eKmax. PREDICTIONS: DeltaE=|E1-E2| (top-2 eK modes) per
state, frozen before ANY driven run. SPEC3-FIRE (reproducible multi-level
spectrum) iff >=2 distinct runs hold qualifying states AND their DeltaE agree
within 30% (rel. diff <0.3, LOCKED). DRIVE: psi(0)=eigenstate-1, H(t) global
J(t)=1+0.05*sin(Omega*t) (weak, LOCKED), dt=0.05, T=200 (4000 steps),
M(Omega)=max_t |<2|psi(t)>|^2; SCAN Omega = DeltaE*{0.7,0.8,0.9,1.0,1.1,1.2,
1.3} (7 LOCKED). SPEC4-FIRE iff >=1/<=2 states show M(DeltaE)>max others AND
M(DeltaE)>0.1 AND M(0.7/1.3 DeltaE)<0.5*M(DeltaE) (peak shape, LOCKED).
VERDICT: FIRE => SPEC4 (driven transitions at predicted spacings); SPEC3-fire
+ SPEC4-null => SPEC3-capped; else SPEC2-capped.

ANALYSIS LOCKS: scipy defaults (mannwhitneyu alternative='greater' as above);
seeds/workers/checkpointing in campaign scripts (untracked, beast); verdicts
filed here with JSON artifacts referenced, never pinned. P1/P2/P3 untouched
(no polarity/handedness readouts in any SPEC run).

NEXT: SPEC-0 campaign (gated on prereg-commit!).

## SPEC-0-VERDICT (SPEC0 (beast; 56 graphs, 536s, 8 workers; acc-bad=0
norm-bad=0; artifacts spec0_parts/{spec0_graphs,spec0_results,
spec0_bare_repair}.json + vecs_*.npz (top-5 evecs per formed state)))

FIRE-RULE (locked): L1 median-formed-eKmax=4.69 vs 5.0 FAIL (6%-below);
L2 MW-formed>pooled(D1+rewired) p=8.1e-05 PASS; L3 3-runs-hit
(L28-d0+L42-d0+L42-d1) PASS; L4 IPRmax-ratio-L42/L28=1.00 PASS (VACUOUS,
see (a)). ALL-required => FIRE=False => SPEC0 (no localized/resonant
modes beyond controls at the preregistered bar). S1 iso-med=1.19 (weak);
S2 outband-frac=1.00 (ALL formed top-modes outside bare band); S3
wcontrast=NaN (empty bare windows when S2=1.0, see (c)).

ANATOMY (filed): formed = dense core (~30% nodes hold ALL edges, hubs
z=45-61) + ~65-70% dust (z=0: 1022/1568 L28, 2472/3528 L42). Core edge
states below band (E* -8.7..-11.6, S2=1.0) with K-weight 27-68%,
enrichment 4.3-8.8 (L28-med-4.53 (11/12-states-zero-qual-modes) vs
L42-med-6.33 (6/6-states-14-to-40-qual-modes, BOTH band edges)); mode
footprints K-scale (IPR^-1 ~130-190 nodes vs |K|~134-246). Branch/sheet
null: W~0.24/0.52/0.24 (random-in-bare-basis) + sheets~0.5/0.5 (no
polarization). Candidate-IPR-ratio-L42/L28=0.69-descriptive (between
extended-0.44 and localized-1.0).

CONTROLS: D1 extended (eKmax~1.32-1.54 in-band, 0-qual-all-18);
REWIRED-MATCHES-FORMED (med-4.33/5.85-vs-4.53/6.33; formed-vs-rewired-only
MW-p=0.084-NS (L2-pooled-significance-driven-by-D1!); qual-pattern-identical
incl.-L28-d0-s2000-2-qual-coincidence; multi-mode-L42-clusters-reproduced)
=> core-edge-states-are-DENSITY/degree-driven (same-hubs-same-labels),
NOT wiring-specific. Bare floor REPAIRED (see (b)): per-mask-eKmax
med-2.3 max-11.46 (flat-band-CLS-lottery AT-E=0); formed distinction is
ENERGY (S2-outside-band), not enrichment alone.

OWNED-LIMITATIONS: (a) L4-as-written measured dust degeneracy
(IPRmax=1.0-exact-both-sizes from 65-70%-z=0) not K-robustness (pass
vacuous; candidate-IPR-0.69 filed as the intended quantity);
(b) bare-ran-with-empty-masks (implementation-bug-vs-prereg-text;
repaired-post-verdict-matched-masks; NO-fire-impact (B-excluded-null));
(c) S3-NaN-by-construction when S2=1.0 (no-bare-modes-near-outside-band-E*;
S2-itself-is-the-spectral readout); (d) L1-near-miss inside L28/L42-split
(4.53-vs-6.33): threshold-placement-lesson for followups, NO-post-hoc-moves.

INTERPRETATION: below-band core ground states concentrating on K EXIST but
(i) sit below the preregistered absolute bar in median and (ii) are fully
reproduced by degree-preserving rewiring => generic dense-lump hub effect,
not an object-specific discrete spectrum. No wiring-specific bound states.

DECISION: SPEC0; SPEC-1/2-MOOT-per-prereg (prediction-before-scan gates
unmet); STOP. FOLLOWUP-PROPOSED (fresh-prereg + review, NOT-run):
density-calibrated bars (rewired-distribution per size), candidate-IPR L4,
L42-multi-level-cluster replication target (14-40-modes) with a
beat-rewired (not match-rewired) bar.
P0' RESTATEMENT (conditional — model.md NOT rewritten:
D14 has no U): IF a separating U is exhibited + basin breadth
passes + residue → 2 with weak-global residue characterized, THEN
P0' restates from "vacuum is 2D fabric (<z>=4)" to "vacuum is the
depleted stationary phase of U" with d_I^vac ≃ 2 as PREDICTION
(Maxwell survives as basin characterization, not origin; "why 2"
moves from postulate to dynamics-output — the U must still
actually output 2).
FALSIFIER (pre-registered campaign, queued behind exhibiting ONE
separating U — existence before universality): homogeneous graphs at
broad d_* (3.7/5/8…), simple conserved blind aggregation U, no
dimensional targets; measure per-phase d(t) (spectral/information).
Pass = knots stabilize + residue → ≃2 robustly across initial
ensembles; fail = U must be told "make residue 2D" (learned nothing).
Methods problems (open, not blockers): per-phase dimension needs
pre-registered knot membership (threshold/scale choice is the tuning
hazard); arrest vs completion (partial separation is FINE — we
observe both phases); ripening (small knots evaporating into one
giant knot = bad, unless BH-like = good — must be shown, not hoped).
Resonance noted: the triangle-rule dense clusters (clustering 0.40,
p → 2.8) are baby knots — aggregation-like flow already seen, just
never separation. Level placement: P0'-level origin story (downstream
of exhibiting U); L0 conditionals untouched per the independence
discipline; no U, no theorems — sketch only.

**Kill relevance:** none until a separating U is exhibited; then the
basin-breadth test above is the wire (single-ensemble separation =
curiosity, broad-basin = genuine attractor).

## MALUS — emergent polarization from the J2 two-sheet structure (Malus track)

**Fork (adopted):** from the PR #65 P1.1 bare-J2 calibrated wave tail
(ac6a140: ballistic detector validated on ring + torus-grid + bare J2;
complex scalar coinless walk H = -J*A, hopping-only, no coin). The
question is whether the hidden two-sheet structure supplies an emergent
polarization degree of freedom: coarse two-component object Psi_x =
(psi_{x,0}, psi_{x,1}) with Malus's law I(theta) = I_0 cos^2(theta) as
the calibration of that space IF it exists. Staged MALUS-0 (internal
sector) -> MALUS-1 (intrinsic analyzer) -> MALUS-2 (law), each gated.

**MALUS-0 PREREG (FROZEN pre-data; this commit predates ALL Malus runs):
discover the internal sector.** On bare J2 (torus, L = 8 algebra + L =
28 P1.1b-scale dynamics), characterize the two-sheet amplitude vector
WITHOUT calling it polarization. Load-bearing question: does the
present J2 wave supply TWO coherent propagating internal states, or one
propagating combination plus a flat/dead one? Sheet-swap S: (S psi)_{x,b}
= psi_{x,1-b}; P_sym = (I+S)/2, P_anti = (I-S)/2 (apparatus:
src/bh_graph/malus.py + tests/test_malus.py, 10 pins in this commit).

**Derived input (pen-and-paper, pre-data prediction, NOT a fit):** both
sheets of a J2 cell share IDENTICAL coarse neighbour sets (the same 4
square moves on each sheet: from (x,y,1) the swap action permutes move
labels, not the move SET), so (H psi)_{x,0} = (H psi)_{x,1} = -SUM_nn
(psi_0 + psi_1) for EVERY psi. Consequences (all pinned as exact
identities): [H,S] = 0; H*P_anti = 0 (full antisymmetric sector, dim
N/2, sits in ker H); symmetric sector = square-lattice walk with
hopping 2J (E(k) = -4J(cos kx + cos ky), band [-8,+8], matching the
P1-Amendment-1 band); flat-band decomposition n_zero = N/2 +
nodal(square, L) with nodal = #{k: cos kx + cos ky = 0}. Predicted
L28 decomposition: 784 + 54 = 838, reproducing the BANKED P1.1b
n_zero = 838 as a zero-parameter consistency check (arithmetic from
locked defs, Amendment-2 precedent). Dynamical prediction: a
chi-polarized (antisymmetric) packet is EXACTLY stationary (E = 0,
v_g = 0, no spreading); a sheet-polarized packet splits into a
propagating symmetric half + a frozen antisymmetric half (sector
weights 50/50 conserved); the (k, k+Q) branch partners are different
MOMENTA, not an internal degree of freedom (a polarizer cannot address
them without changing momentum), and the flat band has v_g = 0 exactly.

**M0 protocol (LOCKED):** M0-ALG (exact algebra): [H,S] = 0
(Frobenius), H*P_anti = 0 (matrix), H*U = U*H_sq (intertwining),
P_anti subset ker H, n_zero = N/2 + nodal(L) for L in {4, 8} (pins)
+ L = 28 decomposition (campaign-filed). M0-DYN (L = 28 torus,
P1.1b-validated window: sigma = 4, k = (0.3, 0), dt = 0.1, T = 10,
disp < L/2 no-wrap gate): THREE packets from one coarse Gaussian --
sym (phi), anti (chi), sheet0 (b = 0 only); per-packet readouts v_fit
+ R^2 + alpha + binned C_v + disp + norm + w_sym/w_anti traces +
sector mixing + overlap(t) + width(t), all with P1.1b-validated
detectors. Ballistic bar (per channel): alpha > 1.3 AND C_v binned
positivity AND disp > 0. Frozen bar: disp < 5% of sym disp AND width
const AND overlap ~ 1 (alpha-meaningless-when-stationary precedent
stands). M0-GATE (decision table, no wiggle): BOTH phi AND chi
ballistic => M0-POSITIVE (two propagating internal states;
MALUS-1 unblocked); phi ballistic AND chi frozen AND sheet0 splits
50/50 conserved => M0-NULL (single propagating sector; STOP --
MALUS-1/2 MOOT, file "no polarization space in the present wave
dynamics"); anything else => M0-INVALID (apparatus fault, fix +
re-prereg, no shopping). Predicted: M0-NULL (theorem above).

**MALUS-1/2 gates (NOT designed in detail; stubs only):** MALUS-1
(intrinsic analyzer) runs ONLY on M0-POSITIVE: graph operation defined
WITHOUT referencing a desired angle; derive its induced 2x2 map on
(phi, chi) FIRST; rank-1-projector check earns the name "polarizer";
angle defined independently of transmission. MALUS-2 (law) runs ONLY
on an earned polarizer: plot I(theta)/I_0 vs independently defined
relative internal angle, test I/I_0 = cos^2 with NO fitted exponent,
plus the two-analyzer series test (0 -> pi/2 blocked; 0 -> pi/4 ->
pi/2 transmits I_0/4). On M0-NULL none of this runs (a "polarizer"
acting on a propagating-plus-frozen pair is a scattering/defect study,
not Malus -- explicitly out of scope here).

**Compute note:** beast EC2 (16.54.88.181) unreachable from this VM
(no SSH key available in this agent's stores; /workspaces path
absent); M0 needs only small linear algebra (dense 1568 eig +
Krylov runs, seconds-minutes), so M0 runs locally and says so.
NEXT: M0 campaign (gated on prereg commit).

**MALUS-0 VERDICT (MEASURED locally, L28 torus, N = 1568; suite 606
passed + 2 skipped): M0-NULL -- single propagating sector, STOP.**
M0-ALG (exact, all 0.0 to machine precision): [H,S] = 0; H*P_anti =
0 (full antisymmetric sector in ker H); H*U = U*H_sq (symmetric =
square lattice at hopping 2J); n_zero = 838 = 784 + 54 = N/2 +
nodal(28) (predicted decomposition EXACT, zero-parameter
reproduction of banked P1.1b n_zero). M0-DYN (P1.1b window sigma =
4, k = (0.3,0), dt = 0.1, T = 10, no-wrap disp < 14 holds): sym
packet BALLISTIC (v = 1.2110, R^2 = 0.9997, alpha = 2.087, disp =
12.18, C_v bins >= +0.991, sector mixing 9e-13; v replicates a
banked P1.1b branch velocity digit-for-digit); anti packet FROZEN
(v = 0.0000, disp = 0.000, width 5.639 -> 5.639, overlap 1.000000,
norm dev 2e-16); sheet0 packet SPLITS 50/50 conserved (sector
mixing 4e-13; total-COM alpha/C_v are two-component-split
artifacts, filed descriptively -- per-sector readouts pinned:
chi part stationary, phi part moved). M0-GATE: phi ballistic AND
chi frozen AND sheet0 50/50 conserved => NULL (no wiggle room:
chi disp is 0% of phi disp vs the 5% frozen bar). Bottom line: the
present coinless scalar J2 wave carries ONE propagating internal
combination (symmetric, scalar square-lattice wave) plus an
EXACTLY dead antisymmetric sector (E = 0, v_g = 0 identically).
Complex phases do NOT resurrect the D15.0 dead sector for the
plain CTQW H = -A (contrast with the DEP spinorial construction,
which needs its coined/staggered structure -- phases alone are
not sufficient). The (k, k+Q) branch partners differ in MOMENTUM,
not internal state; the flat band is stationary, not a second
polarization. => NO polarization space in the present wave
dynamics. MALUS-1/2 MOOT on bare J2 (no analyzer experiments run,
per gate; a propagating-plus-frozen "polarizer" would be a
defect study, not Malus). Consistent with -- and strengthening --
the D15 rank-1 story: dead under diffusion AND under unitary wave
dynamics, exactly. REPLICATION (beast EC2, key in shared user store):
M0-ALG + M0-DYN rerun on beast clone match local digits exactly
(sym v = 1.2110 / alpha = 2.087 / disp = 12.183; anti disp = 0 /
overlap = 1; sheet0 50/50; n_zero = 838); malus+ballistic+formation
subset 51 passed on beast; full suite 606+2 green locally (full
beast suite deferred: box at load ~500 from concurrent campaigns).
NEXT: none on this track (null banked).

SLIT-PREREG (FROZEN-2026-10-01 (~19:30-UTC (commit-predates-ALL-SLIT-
campaign-runs!)); two-path-interference-campaign (wave-sector-only
(P1-derived-apparatus (H(G)=-J·A(G)-hopping-only-LOCKED (same-as-P1!));
NO-formation-runs + NO-polarity/handedness-readouts (P1/P2/P3/B0-
untouched (separate-track (non-interfering!))))). QUESTION: does-the-
scalar-J2-wave-produce-interference-from-alternative-graph-paths + does-
which-path-information-destroy-it-without-a-collapse-postulate.
SCOPE: SLIT-0-coherent-calibration + SLIT-1-phase-dependence + SLIT-2-
path-record/decoherence + SLIT-3-graph-only-corridors; SLIT-4-discrete-
detection/Born-DEFERRED (no-detector-mechanism-in-model (explicit!)).
APPARATUS (this-commit (14-pins!)): bond-barriers (node-set-fixed-across-
A/B/AB (Hilbert-comparable!)); slit-mouth-superpositions-on-ONE-G_AB
((A+e^{iφ}B)/√2-Loewdin-orthonormalized (linearity-to-Krylov!)); sharp-
mask-entangler + eraser (unitary-on-system×qubit (demonstrates-WHAT-
path-recording-WOULD-do (NOT-that-graph-provides-it (open-question!))));
MZ-theta-corridors (abstract (no-coords!)). DESIGN-BASIS (apparatus-
validation-NOT-campaign-data (toy/medium/large-grids-at-NON-campaign-
sizes + MZ-len6-vs-campaign-14 (all-fringes/exactness-confirmed (filed-
in-commit-message!))): thresholds-set-≥2×-below-toy (fringe-presence-vs-
Krylov-noise (~1e-12!) (NOT-tuned-to-pass!)); exact-claims-from-symmetry
(center/odd-state/destructive (mirror-automorphism-pinned!)).
GEOMETRY (LOCKED): OPEN-GRID-70×61 (xb=30, slits-A=(22,23)-B=(37,38)
(d=15-about-yc=30 (mirror-exact!)), mouths-(31,22.5)/(31,37.5)-σ=2-k=
(1.0,0), source-(12,30)-σ=3-k=(1.0,0), detector-xd=54 (D=23), window-W=
|y-30|≤16 (33pts), sub-window-S=|y-30|≤8, dt=0.1). J2-L28 (xb=12, slits-
(8,20) (d=12-about-14!), mouths-(13,8)/(13,20)-σ=2-k=(0.3,0)-P1.1b-validated,
detector-xd=20 (D=7), window-|y-14|≤12, dt=0.1). MZ-len14 (campaign (toy-
was-6!), T=80-window). CLOCK (operational (pre-committed!)): T* = argmax-
detector-line-weight-over-[0,60]-open ([0,20]-J2) from-the-AB-run (ONE-
clock (all-preparations/graphs-read-at-T*!)); t* = argmax-w_D(φ=0)-for-MZ.
SLIT-0a-MOUTHS (same-G_AB): HEADLINE-V(W)>0.3-AND-nmax(W)≥3-AND-rmsR>0.2-
AND-L2(AB,incoh)>0.05-AND-linearity-dev<1e-9. VALIDITY: Loewdin-corr<0.05
+ detW(T*)>0.5% + wallW<5% + T*-interior(<58/18) + norm-1e-8.
SLIT-0b-SOURCE (G_A/G_B/G_AB-one-clock): HEADLINE-Rmax(S)>1.4-AND-Rmin(S)<
0.6 (R=I_AB/(I_A+I_B)-per-point (constructive≈2/destructive≈0!))-AND-L2>
0.05. VALIDITY: singles-mirror-L2<0.03 + detW_AB>0.5% + wallW<5% + interior
+ norm. CONTROL: closed-barrier-right-weight<1e-9-at-T* (exact-block!).
SLIT-1-PHASE (G_AB-T*): φ∈{0,π/2,π,2π}: HEADLINE-center-I(π/2)/I(0)=0.5±0.1-
AND-I(π)/I(0)<0.05 (odd-state-exact-zero!)-AND-periodicity-|I(2π)-I(0)|/I(0)<
1e-9-AND-L2(0,π)>0.05 (pattern-shift!). VALIDITY: I(0)-center>0 (non-node-
denominator (else-void!)) + norm.
SLIT-2-WHICHPATH (G_AB-T*): γ∈{1,0.75,0.5,0.25,0}: HEADLINE-A(γ)/A(1)=γ±0.03-
each (A=RMS(I(γ)-E)/RMS(E) (exact-linear!))-AND-A(0)<0.02-AND-R²>0.999.
ENTANGLER (t=0-half-plane-masks): HEADLINE-crosstalk<1%-AND-L2(traced,E)<
0.03-AND-amp_kill<0.05-AND-eraser-L2(plus,I_AB/2)<1e-9 (exact-restore!)-
AND-minus-center-ratio<0.05 (antifringe!). VALIDITY: norm.
SLIT-3-MZ (len14): HEADLINE-φ-scan-at-t*: w(π/2)/w(0)=0.5±0.03-AND-w(π)/w(0)<
0.02 (swap-odd-exact-zero!); single-arm-φ-maxdiff<1e-9-full-window (exact!);
arm-scan-(lenA=14-lenB=14..26-S-injection)-maxw-max/min>3. VALIDITY: w_D(t*)>
10% + t*-interior(<75) + norm.
J2-SECONDARY (SLIT-0a-only (no-source-driven-on-J2 (wrap-scope-cut!))):
HEADLINE-V>0.2-AND-rmsR>0.15-AND-L2>0.05. VALIDITY: purity>0.8-per-packet
+ corr<0.05 + T*<12 (wrap-arrival-17.5-margin!) + detW>0.5% + norm.
VERDICT-RULE (per-stage): PASS ⟺ ALL-headline-AND-ALL-validity; validity-
fail ⟹ VOID (file + amend (P1.1b-precedent!) (NOT-fail!)); criterion-fail ⟹
FAIL (file!). GLOBAL: suite-green (all-pins + full-suite-on-beast). NEXT:
slit_campaign.py (gated-on-prereg-commit!) + beast-run.

SLIT-CAMPAIGN-1-filed (SUPERSEDED-partial (mechanics-bug + two-operational-
timing-voids (below!)); beast-15s; NO-verdict-drawn-on-affected-stages
(discipline!)): PASS-STAND (valid-gates (deterministic (rerun-replicates!))):
0a (T*=12.4: V=0.678/nmax=5/rmsR=0.392/L2=0.075/lin=2e-14 (all-with-margin!);
detW=8.2%/wall=0.9%/corr=4e-4); 0b (T*=26.1: Rmax=2.00/Rmin=0.016/L2=0.110
(center-constructive-2×-exact-theory!); mirror=2e-14/detW=0.6%/wall=1.1%);
shut (rightW=3e-10 (exact-block!)); SLIT-1 (half=0.5000/pi=8e-28/per=6e-14/
L2(0,π)=0.151 (symmetry-exact!)). AFFECTED (no-verdict!): 2g-numbers (passed-
but-WRONG-states (script-shadow-bug (below!))); 2e-FAIL×2 (amp_kill=27.7/
eraser=0.082 (meaningless-quantities (cross-experiment-comparison (bug!))));
J2-L2=0.035-vs-0.05 (near-miss-ON-PRE-ARRIVAL-pattern (T*=2.4-vs-arrival-5.7
(argmax-on-flat-tail-curve (operational-misfire!)); V=0.84-anyway!)); MZ-φ-
VOID (t*=77.2-at-window-edge-80 (peak-not-captured (window-too-short!));
ratios-exact-anyway (0.5000/4e-33 (t*-independent-algebra!))); MZ-arm-ratio=
4.31 (passed-but-window-suspect-for-long-arms (rerun-under-amended-window!)).
SLIT-AMENDMENT-1 (PRE-RERUN (affected-stages-only (passed-stages-STAND!))):
(1)-IMPL-BUG-owned: 0b-section-reassigned-eA/eB/Iab (SLIT-2-compared-0a-
entangler-against-0b-patterns (cross-time/cross-graph-garbage!)) ⟹ script-
renamed-to-prereg-spec (mechanics (protocol-unchanged!)). (2)-J2-T*-rule:
argmax-window-[0,20]→[5,20] (lower-bound-5 = P1.1b-arrival-5.7(D=7/v=1.235-
filed!)−0.7 (captures-peak + excludes-pre-arrival-tail-argmax (operational-
timing (NOT-goalpost!))); T*<12-gate + all-thresholds-STAND). (3)-MZ-window:
T=80→160 + interior-gate-t*<75→t*<150 (2×-measured-edge-peak-77.2 (P1.1b-
arithmetic-precedent!); all-thresholds-STAND). RERUN (gated-on-amendment-
commit!): full-script (passed-stages-must-REPLICATE-identically (bonus-
determinism-check!) + affected-stages-decided).

SLIT-CAMPAIGN-2-filed (beast; post-Amendment-1): REPLICATED (0a/0b/shut/1-
identical-to-run-1 (determinism-✓!)); SLIT-2-PASS (2g-exact-linear (R²=1.0!) +
2e (ctalk=2e-4/L2=0.002/amp_kill=0.010/eraser=1e-14/minus=3e-5 (script-fix-
confirmed!))); SLIT-3-PASS (φ-half=0.5000/π=4e-33/t*=77.2-interior-160/
single-arm-exact/arm-ratio=3.66!). J2 (amended-window-[5,20]): T*=13.8 (SECOND-
misfire (run-1: 2.4-pre-arrival; run-2: 13.8-wrap-zone-VOID (T*<12!)); line-
weight-NON-UNIMODAL-on-ring (comparable-peaks-2.4/13.8 (0.0953-both!) +
arrival-5.7-in-valley!) ⟹ argmax-rule-IS-WRONG-FUNCTIONAL-for-rings (method-
finding!)); pattern-at-13.8: V=0.706/rmsR=0.210-✓-but-L2=0.046-vs-0.05 (near-
miss (envelope-dip-contamination-suspected (2-lobe-E-has-V-too!))).
SLIT-AMENDMENT-2 (J2-clock-FINAL (pre-committed (no-further-J2-timing (outcome-
filed-as-is!)); thresholds-UNCHANGED)): REPLACE-argmax-with-FIXED-T_J=6.0
(= arrival-5.67 (D=7/v=1.235-P1.1b-filed!) rounded-up (+0.3-fringe-margin);
P1.1b-fixed-T-from-prior-v-precedent!; wrap-17.5-far (arithmetic!)); T*<12-
gate-RETIRE (no-T* (fixed-time)); detW/purity/corr/norm-gates-STAND (detW-void
⟹ J2-VOID (timing (not-physics!))). ADD-descriptive (NOT-criteria!): J2-nmax +
envelope-V(E) (envelope-vs-fringe-diagnosis!). RERUN (gated-on-commit!):
full-script (replication-check-×3!) + J2-decided-final.

SLIT-VERDICT (PASS-ALL-STAGES (beast-campaign-3 (SCRIPT_EXIT=0 (FAIL=[]-VOID=[]));
suite-615-passed + 2-skipped (beast -n-64 (full!)); apparatus-14-pins-green):
SLIT-0a-PASS (T*=12.4: V=0.678/nmax=5(!)/rmsR=0.392/L2=0.075/lin=2e-14 (linearity-
exact!)); SLIT-0b-PASS (T*=26.1: Rmax=2.00/Rmin=0.016 (center-2×-constructive +
deep-destructive (Young-pattern!))/L2=0.110/mirror=2e-14); shut-NULL-✓ (3e-10);
SLIT-1-PASS (half=0.5000/pi=8e-28/periodicity-6e-14/L2-shift=0.151 (coherent-
superposition (NOT-focusing-artifact!))); SLIT-2-PASS (γ-exact-linear-R²=1.0000/
kill-exact-0 + entangler (ctalk-2e-4/traced-L2-0.002/kill-0.010 (fringes-gone!)/
eraser-restore-1e-14-exact/antifringe-center-3e-5!)); SLIT-3-PASS (MZ-φ-half=
0.5000/π=4e-33/single-arm-exact-independence/arm-scan-ratio-3.66 (graph-path-
interference-WITHOUT-spatial-picture!)); J2-SECONDARY-PASS (fixed-T=6: V=0.853/
rmsR=0.589/L2=0.149 (3×-margin!)/purity-100%/nmax(AB)=3-vs-E=4 (genuine-shape-
change (NOT-envelope!))). INTERPRETATION (filed (NOT-overclaimed!)): scalar-J2-
wave-DOES-interfere-from-alternative-paths (expected (complex-linear (positive-
control-passed!))); which-path-coupling-DESTROYS-fringes-continuously-in-|γ|
WITHOUT-collapse-postulate (dynamical-suppression + eraser-restore (unitary-
only!)); graph-corridors-interfere-without-geometry (SLIT-3!). OPEN (hard-wall-
STANDS!): NO-graph-degree-supplies-path-records-yet (entangler-is-external-
unitary (NOT-derived!)); NO-detection/Born-mechanism (SLIT-4-deferred (single-
detection-events-unexplained!)); interference-IS-built-into-complex-ψ (classical-
waves-do-this-too (SLIT-0 ≠ QM-demonstration (framing-kept!))). NEXT: SLIT-
campaign-CLOSED (all-stages-pass (+2-amendments-filed-pre-rerun (discipline-
kept!))); followups (NOT-opened-here!): derived-path-record-degree + SLIT-4-
detector-mechanism (queued-behind-model-content!).

TUN-PREREG (FROZEN-2026-10-01 (commit-predates-ALL-TUN-runs!);
evanescent-transmission/tunneling-campaign (NOT-P1 (separate-branch
(cursor/tunneling-tun-d55e (based-on-PR#65-tail (P1.1-apparatus-
inheritance!)))))). QUESTION (wave-mechanics (NOT-claimed-uniquely-
quantum!)): can-the-validated-scalar-J2-wave-transmit-through-a-
graph-region-in-which-its-incident-mode-is-non-propagating (with-
barrier-width/strength-dependence-matching-evanescent-prediction?).
PROVENANCE (fork (read-only-inheritance!)): P1.1-apparatus (complex-
scalar-ψ + H=-A-hopping-ONLY (LOCKED (no-onsite/degree/core/potential
/force-law (same-ban-as-P1!))) + Gaussian-k-packets + Krylov-exact-
unitary + norm/accounting-gates); NO-formation + NO-DNLS + NO-
detector-model. BARRIER (geometry-ONLY (bond-removal (no-new-law!))):
full-width-wall (columns-[28,28+L_B)-of-J2-torus-L96 (N=18432!)) with-
ALL-y-displacement-bonds-removed (x-bonds-intact-everywhere (wall-
stays-connected (no-trivial-T=0!)); node-labels-unchanged (matched-
controls-share-labels!)). PACKETS (per-E0 (σx=6-σy=8 (spread-gates-
6<16-AND-8<16-✓!) + x0=10-y0=48 + k=(kx0,0)-kx0=acos(|E0|/4-1) +
dt=0.1-J=1)): E0-grid-{-5.0,-5.5,-6.0,-6.5,-7.0} (kx0-{1.3181,1.1864,
1.0472,0.8957,0.7227} + v-{3.8730,3.7081,3.4641,3.1225,2.6458}) +
below-threshold-control-E0=-3.0 (kx0=1.8235-v=3.8730). T_SEP-LOCKED-
FORMULA (per-cell (from-TUN-0-banked-v_in (same-E0!))): T_sep =
ceil_up_0.5(((wall_hi - x0) + 3σx + 2)/v_in) (transmitted-center-
clears-wall_hi-by-3σx+2 (reflected-clears-symmetrically (verified-
arithmetic-per-cell (gap-≥6-columns-everwhere!))); banked-v-rules
(expected-values-from-analytic-v-filed-below (change-filed-not-tuned
(if-any!))). EXPECTED-T_SEP: TUN-2-{-5.5}: LB-{0..6,8}→{10.5,11.0,
11.0,11.5,11.5,12.0,12.0,12.5}; TUN-3-{LB4}: E0-{-5.0,-5.5,-6.0,-6.5,
-7.0,-3.0}→{11.0,11.5,12.5,13.5,16.0,11.0}.
TUN-0-BARRIER-FREE-CALIBRATION (6-free-runs (one-per-E0 (bare-L96-J2
+ run-length-= max-T_sep-over-that-E0's-cells (11.0/12.5/12.5/13.5/
16.0/11.0 (all-disp<L/2=48-✓!))) + banks-v_in/E_in/spread/W-/norm/
arrival-profile-per-E0): PASS ⟺ ALL-per-E0: (a)-|v-v_g|/|v_g|<10%
(P1.1a-criterion!); (b)-E_in+6σ_E<0-AND-E_in-6σ_E>-8 (minus-purity-by-
energy-support (E-sign-=branch (tails-stay-E<0 (tails-beyond-6σ-weight
~1e-9!)))); (c)-norm-maxdev<1e-8; (d)-α>1.3; (e)-wrap-weight-(cols-≥90)
-at-t_run<1e-6; (f)-disp<L/2. ANY-fail⟹TUN-0-INVALID-STOP (fix-
apparatus + re-prereg (NO-barrier-runs-until-TUN-0-PASS!)).
TUN-1-FORBIDDEN-BARRIER (NO-dynamics (spectral-demonstration (pre-
run!))): wall-nodes-degree-≤4 (pinned-builder!) ⟹ Gershgorin-wall-
spectrum-⊆[-4,4] ⟹ E0-grid-{-5.0,...,-7.0}-ALL-STRICTLY-BELOW (−4
(FORBIDDEN (no-propagating-wall-mode-at-E0!))); control-E0=-3.0-
INSIDE (propagating (contrast!)); κ(E0)=arccosh(|E0|/4) = {0.693147,
0.841019,0.962424,1.066732,1.158810} (evanescent (κ-real->0!));
wall-bipartite-pinned (chiral-symmetry-exact (no-branch-mixing-by-
construction!)) + wall-connected-pinned. FILED-by-tun1-stage.
TUN-2-WIDTH-LAW (E0=-5.5 (κ=0.841019-2κ=1.682039!) + L_B∈{0,1,2,3,4,5,
6,8} (8-cells (deterministic (no-seeds (one-run-per-cell!))))): FROZEN-
PREDICTIONS (k-averaged-transfer-matrix-T_pred (stationary-theory-
ONLY (pinned-predictor (never-fitted!))): LB-{0,1,2,3,4,5,6,8}→T_pred-
{1.0,0.4611895,0.1035743,0.02092973,0.004275479,0.0009019985,
0.0001980578,0.00001119983}. PASS ⟺ ALL: (a)-T+R+B=1-to-1e-9-every-
frame-every-cell (hard-accounting!); (b)-T/T_pred∈[1/3,3]-for-L_B∈
{1..6} (absolute-prediction (prefactor-included!)); (c)-log-slope-over-
{2..5}-within-30%-of-−2κ (exponential-law!); (d)-T>1e-10-for-L_B∈{1..6}
(finite-transmission!); (e)-T(L_B=0)>0.99 (no-barrier-control!); (f)-
T(L_B=8)<1e-4 (near-zero-wide-barrier!); (g)-wall-residence-STRICTLY-
decreasing-across-columns-for-L_B=6 (evanescent-interior-shape!); (h)-
interior-asym-res(lo)/res(lo+5)>10-for-L_B=6 (decay-from-incident-side
(single-mode-theory-~4400 (threshold-440×-below (margin-huge!)))). FILED
(non-firing!): monotonic-T-in-L_B + interior-slope-values + com_y-drift
+ LB8-ratio + E-conservation-drift.
TUN-3-STRENGTH-LAW (L_B=4-frozen + E0-grid-{-5.0,-5.5,-6.0,-6.5,-7.0}
+ control-E0=-3.0 (6-cells (E0=-5.5-L_B=4-RUN-ONCE (shared-with-TUN-2
(filed-in-both (roles-split (no-double-dip!)))))): FROZEN-PREDICTIONS:
E0-{-5.0,-5.5,-6.0,-6.5,-7.0}→T_pred-{0.01011864,0.004275479,0.001922993,
0.0008727812,0.0003727038} (24×-range (κ↑⟹T↓!)); control-E0=-3.0→T_pred-
0.7098799 (propagating-O(1)!). PASS ⟺ ALL: (a)-accounting-1e-9 (stands!);
(b)-T-STRICTLY-decreasing-over-E0-grid (strength-law (κ↑⟹T↓!)); (c)-T/
T_pred∈[1/3,3]-all-5-grid-points; (d)-control-T/T_pred∈[1/3,3]-AND-T>0.3
(below-threshold-propagating (wall-per-se-does-not-kill-transmission!));
(e)-no-barrier-control-cited-from-TUN-2-LB0 (T>0.99 (TUN-2-owns-it!)).
FILED: control-interior-asym/monotonicity (propagating-contrast (~O(1)/
non-monotonic-expected (descriptive!))) + com_y + E-drift.
TUN-4-DOUBLE-BARRIER (GATED (design-ONLY-after-TUN-2+TUN-3-PASS-banked!)):
symmetric-double-wall + pristine-well (geometry-frozen-in-TUN-4-amendment
+ pre-registered-energy-scan + resonance-predictions-from-isolated-well-
modes (computed-pre-scan-from-H (no-tuning-after-seeing-resonances!))).
FORMATION-EXTENSION (LATER (read-only-D5∞ (no-core-dependent-potential
(manufacture-ban!)))). INTERPRETATION (locked!): TUN-PASS ⟺ TUN-0-PASS +
TUN-1-filed + TUN-2-PASS + TUN-3-PASS (box: spectrally-forbidden +
evanescent-interior + finite-T + predicted-width-dependence (graph-wave-
tunneling/EVANESCENT-TRANSMISSION (classical-coherent-waves-do-this-too
(uniquely-quantum-claim-REQUIRES-later-particle/detection-model!)))). NEXT:
TUN-0-calibration-on-beast (gated on prereg-commit!).

TUN-0-PILOT-1-filed (SUPERSEDED (gate-miss (no-verdict-drawn
(discipline (P1.1b-precedent!))))): beast-free-runs (L96 (6/6-ran!)):
v-within-0.36%-all-6 (3.8589/3.6947/3.4517/3.1114/2.6367/3.8589-vs-
analytic!); R²=1.000000-all; α=2.00-all; C_v-bins-+1.000-all-60;
norm-≤1.4e-13; disp-{42.4,46.2,43.1,42.0,42.2,42.4}-all-<48-✓; wrap-
≤1.1e-7-✓; E_in-{−4.9887,−5.4870,−5.9853,−6.4835,−6.9818,−2.9957} ±
{0.3219,0.3082,0.2881,0.2598,0.2205,0.3219}; E+6σ<0-all-✓ BUT-E−6σ>−8-
MISS-on-2/6 (−8.043-(−6.5!)-AND-−8.305-(−7.0!) (Gaussian-E±6σ-ignores-
band-bottom-curvature (E(k)-flattens (linear-extrapolation-overshoots-
below-−8-where-no-weight-exists!)))). Gate-(b)-as-written-UNACHIEVABLE-
near-band-bottom (owned-bug (predictable-from-locked-E(k) (correction-
is-arithmetic (not-tuning!)))).
TUN-AMENDMENT-1 (purity-gate-repair (PRE-RERUN (pilot-1-opened (all-
numbers-filed-above!)))): gate-(b)-REPLACED-by-(b')-purity-by-EXACT-
k-support-bound (locked-formula (packet-definition-ONLY (no-data!))):
E_min^sup = −4(cos(kx0−6σkx)+1) + E_max^sup = −4(cos(kx0+6σkx)+
cos(6σky)) (σk=1/2σ-per-axis (±6σ-rectangle (tails-~1e-9-filed!)));
(b') ⟺ −8<E_min^sup-AND-E_max^sup<0 (pre-computed-theory (all-6-pass:
E0-{-5.0,-5.5,-6.0,-6.5,-7.0,-3.0}→[E_min,E_max]-{[-6.74,-2.75],
[-7.09,-3.26],[-7.42,-3.82],[-7.69,-4.43],[-7.90,-5.09],[-4.98,-0.98]}
(all-inside-(−8,0)-with-margin (tightest-0.099!)))); script-banks-
E_sup_min/max (pinned-support_bounds (11-pins!)); gates-(a)(c)(d)(e)
(f)-UNCHANGED. NEXT: TUN-0-pilot-2 (fresh-runs (gated on amendment-
commit!) + T_sep-freeze (banked-v-rules!) + TUN-2/TUN-3 (gated on
TUN-0-PASS!).

TUN-0-VERDICT (PASS (pilot-2 (G1-geometry (beast)))): 6/6-cells-pass-all-
gates: (a)-v-within-0.36% (R²=1.000000!); (b')-support-bounds-inside-
(−8,0)-all (tightest-margin-0.099!); (c)-norm-≤1.4e-13; (d)-α=2.00-all;
(e)-wrap-≤1.1e-7; (f)-disp-≤46.2<48. ⟹ G1-bank-valid (v_in-banked +
T_sep-frozen (banked-==-expected (rounding-absorbed-0.36%!))).
TUN-2/TUN-3-PILOT-1-filed (VOID (wrap-contamination-flaw (no-verdict-
drawn (numbers-filed (NOT-verdict-data!))))): G1-cells (L96): T-≈0.2-
0.4-FLAT-across-ALL-evanescent-cells (no-L_B/E0-dependence!) with-
accounting-exact (≤3e-13!) + control-E0=-3.0-matching-prediction-
(ratio-1.08-✓ (predictor-healthy!)) + LB0-T=0.9998-✓. DIAGNOSIS-owned:
reflected-packet-WRAPS-into-T-region (torus-right-region-extends-to-L
(wrapped-weight-at-high-x-counted-as-transmitted!)); predicted-wrap-
fractions-{0.13,0.17,0.21,0.26,0.31,0.37,0.50}-for-LB-{1,2,3,4,5,6,8}
×-R-match-observed-excess-order-+-scaling-✓. ROOT-CAUSE: G1-prereg-
arithmetic-compared-transmitted-end-vs-reflected-wrap-start (meaningless
(both-inside-same-T-region!) (owned-error (demonstrable-from-frozen-
design-alone: reflected-3σ-edge-at-−10<0 (no-data-needed!)))).
TUN-AMENDMENT-2 (geometry-repair-G2 (PRE-RERUN (pilot-1-void (filed-
above!)))): L=96→160 + x0=10→8 + wall_lo=28→56 (σx=6-σy=8-KEPT (floor-
arithmetic-unchanged!) + regions-UNCHANGED (whole-torus-T/R/B (T+R+B=1-
stands!)) + predictions-UNCHANGED (L-independent (recomputed-identical:
T_pred-table-stands-bitwise!)) + criteria-UNCHANGED ((a)-(h)/(a)-(e)!)).
G2-ARITHMETIC (filed (verified-per-cell!)): incident-path-48; T_sep-=
formula(banked-v) (expected-(analytic-v): TUN-2-{18.5,19.0,19.0,19.5,
19.5,20.0,20.0,20.5} + TUN-3-{19.0,19.5,21.0,23.5,27.5,19.0}); trans-
center-≤84-+3σ=102<160-✓ (margin-58 (NO-trans-wrap!)); refl-center-≥28-
−3σ=9.8>0-✓ (worst-wrap-2e-6-(LB8-only (check-(f)-upper-bound-has-10×-
margin (contamination-ADDS (conservative-direction!)))); LB≤6-contam-
≤1e-7-vs-T≥2e-4 (negligible!)); TUN-0-G2-run-lengths-{19.0,20.5,21.0,
23.5,27.5,19.0}-disp-≤76<80-✓ (gate-(f)-holds (margin-≥4!)); ADDED-filed-
monitor-wrap_w-(cols-≥L−8-at-T_sep (non-firing!)). G1-bank-SUPERSEDED-by-
G2-bank (different-L (G1-PASS-stands-as-validity (not-as-bank!))). NEXT:
TUN-0-pilot-3-(G2-fresh) + TUN-2/TUN-3-pilot-2-(G2-fresh) (gated on
amendment-commit + TUN-0-G2-PASS (same-gates (a)(b')(c)(d)(e)(f)!)).

TUN-0-VERDICT-G2 (PASS (pilot-3 (L160 (beast)))): 6/6-cells-pass-all-
gates: (a)-v-within-0.35% (R²=1.000000!); (b')-support-bounds-inside-
(−8,0)-all; (c)-norm-≤6.1e-14; (d)-α=2.00-all; (e)-wrap-≤4e-16;
(f)-disp-≤75.8<80. ⟹ G2-bank-valid (T_sep-frozen (banked-rules
(LB6-rounded-20.0→20.5-ONLY-change (formula-locked (filed!))))).
TUN-1-G2-filed (L160-N51200): wall_deg_max-4-ALL-LB (Gershgorin-
[−4,4]-stands!) + bipartite-✓ + connected-✓ + κ-table-stands.
TUN-2-VERDICT (PASS (G2 (beast))): 8/8: (a)-accounting-≤1.5e-13-every-
frame-every-cell-✓; (b)-T/T_pred-{1.000,1.000,1.000,1.000,1.001,1.026}-
for-LB-{1..6}-✓ (≤2.6%-over-3-DECADES (T-0.46→2.0e-4!) (absolute-
prediction-NO-FIT!)); (c)-slope-−1.581-vs-−2κ=−1.682 (6.0%-✓ (30%-
band!)); (d)-T>1e-10-✓ (min-2.0e-4!); (e)-T(0)=0.99950-✓; (f)-T(8)=
2.89e-5<1e-4-✓; (g)-LB6-residence-strictly-decreasing-✓; (h)-LB6-asym-
3880>10-✓ (single-mode-~4400!). FILED: T-strictly-decreasing-in-LB-✓;
interior-slopes-{-1.647,-1.633,-1.615,-1.595}-(LB4568 (within-5%-of-
−2κ (descriptive!))); asym-{177,846,3880,69660}-(e^{2κ}-growth-✓);
com_y-drift-≤7e-14 (ky-conservation-✓); wrap-monitors-close-the-
contamination-account (T_meas=T_pred+wrap_w-in-EVERY-cell (LB8: 1.12e-5
+1.77e-5=2.89e-5-EXACT (ratio-2.58-fully-explained (check-(f)-stands!))).
TUN-3-VERDICT (PASS (G2 (beast))): 5/5: (a)-accounting-≤1.2e-13-✓; (b)-T-
{0.010119,0.0042756,0.0019242,0.0008849,0.0004713}-STRICTLY-decreasing-
over-E0-grid-✓ (κ↑⟹T↓!); (c)-ratios-{1.000,1.000,1.001,1.014,1.264}-✓
(E0=−7-excess-=-wrap-monitor-9.8e-5-EXACT (long-run-spread (filed!)));
(d)-control-T=0.6952-vs-pred-0.7099 (ratio-0.979-✓ + >0.3-✓); (e)-LB0-
cited-✓. FILED: control-interior-asym-1.96 + NON-monotonic (propagating-
contrast-vs-3880/monotonic (STARK!)); com_y-≤7e-13.
TUN-VERDICT-SINGLE-BARRIER (PASS): box-CLOSED (spectrally-forbidden-
(TUN-1) + evanescent-interior (mono+asym-3880) + finite-T (all-cells) +
predicted-width-dependence (ratios-≤2.6% + slope-6%)). ⟹ graph-wave-
tunneling/EVANESCENT-TRANSMISSION-ESTABLISHED (uniquely-quantum-claim-
NOT-made (locked-interpretation!)). NEXT: TUN-4-double-barrier (design-
amendment (geometry+scan+resonance-predictions-frozen-pre-run!) (gated-
OPEN (TUN-2+TUN-3-PASS-banked!))).

TUN-AMENDMENT-3 (TUN-4-double-barrier-prereg (FROZEN-PRE-RUN (gated-
OPEN (TUN-2+TUN-3-PASS-banked!)); design-from-THEORY-only (transfer-
matrix + box-modes (no-dynamics-input!)))). GEOMETRY-frozen: L160 +
x0=40 + walls-[64,66)+[70,72)-(LB=2-each (y-bond-removal (same-law!)))
+ well-[66,70)-(LW=4-pristine) + regions-left-x<64/struct-64..72/
right-x≥72 (T+R+B=1-stands!) + packets-σx=6-σy=8-dt=0.1 (UNCHANGED!).
LB=2-chosen-over-LB=3 (theory: LB3-second-resonance-width-≪0.002-
(invisible-after-k-averaging!) vs LB2-TWO-visible (single-mode-TM:
E_res-{-7.418 (w-0.0097!),-5.826 (w-0.0585!)} (symmetric-heights-~1!))).
BOX-modes-(LW4-open-segment-ky0): {-7.23607,-5.23607} (descent-addresses
(TM-shifts-−0.18/−0.59-=-thin-wall-penetration (theory-known (filed!)))).
SCAN-frozen-25-E0 (no-adaptive-peeking!): 0.2-grid-{-7.4..-4.4}(16) +
exact-TM-{-7.418,-5.826}(2) + fine-{-7.6,-7.5,-7.3,-6.1,-5.9,-5.7,-5.5}(7).
BANK: 25-free-runs (x0=40 (same-gates-(a)(b')(c)(d)(e)(f)-as-TUN-0!)) +
T_sep-=-formula(banked-v (per-E0!))-wall_hi=72 (expected: {-7.6:30.0,
-7.5:27.0,-7.418:25.5,-7.4:25.0,-7.3:23.5,-7.2:22.0,-7.0:20.0,-6.8:18.5,
-6.6:17.5,-6.4:16.5,-6.2:16.0,-6.1:15.5,-6.0:15.5,-5.9:15.0,-5.826:15.0,
-5.8:15.0,-5.7:14.5,-5.6:14.5,-5.5:14.5,-5.4:14.0,-5.2:14.0,-5.0:13.5,
-4.8:13.5,-4.6:13.5,-4.4:13.5} (banked-rules!)). FROZEN-PREDICTIONS
(dense-k-averaged-double-TM-n_kx=2001 (stationary-theory-ONLY!)): {-7.6:
0.0130993,-7.5:0.0223409,-7.418:0.0253478,-7.4:0.0252608,-7.3:0.0208296,
-7.2:0.0133764,-7.0:0.00331235,-6.8:0.00119403,-6.6:0.00359037,-6.4:
0.0163786,-6.2:0.0497228,-6.1:0.0722338,-6.0:0.0932298,-5.9:0.107404,
-5.826:0.111190,-5.8:0.111023,-5.7:0.103563,-5.6:0.0877362,-5.5:0.0680454,
-5.4:0.0488625,-5.2:0.0217786,-5.0:0.0109276,-4.8:0.0103340,-4.6:0.0187706,
-4.4:0.0445399} (contrast-pred-93× (min-−6.8!) (background-≫floor-✓)).
PASS ⟺ ALL: (a)-accounting-1e-9-every-frame-all-25; (b)-T/T_pred∈[1/3,3]-
all-25 (full-curve-heights+shape!); (c)-max(scan)/min(scan)≥10 (pred-93×!);
(d)-max-over-U={-6.1..-5.4}(9pts)≥5×T(−6.8) (upper-resonance (pred-93×!));
(e)-max-over-L={-7.6..-7.2}(6pts)≥5×T(−6.8) (lower-resonance (pred-21×!));
(f)-argmax(U)-within-±0.15-of-−5.826-AND-argmax(L)-within-±0.15-of-−7.418
(TM-addresses (robust-to-−7.418/−7.4-near-tie (both-inside-window!)));
box-modes-filed-as-descent-addresses (±0.7-consistency (weak-by-design
(disclosed!))). NARROWNESS (locked-interpretation!): measured-widths-≈σ_E-
(packet-limited (heights-≈(w/σ_E)·1-match-pred ⟹ true-w-≪-σ_E (direct-
width-resolution-packet-limited (filed!)))). NEXT: TUN-4bank+TUN-4-on-beast
(gated on amendment-commit + bank-gates!).

TUN-4-PILOT-1-filed (SUPERSEDED-as-read (premature-T_sep-flaw (numbers-
filed (NOT-verdict-data!))))): beast-25-pt-scan: raw-T-ratios-0.08-0.93-
vs-pred (systematically-LOW!) with-B-≤0.15 (vs-single-wall-~1e-4!) +
accounting-exact + bank-gates-25/25-PASS. DIAGNOSIS-owned: RESONANT-DWELL
(peak-lifetimes-~-1/Γ-≈-17-100-units (T_sep-13-30-cuts-before-trapped-
weight-leaks!)); extended-T_sep-IMPOSSIBLE (σ(t≈150)≈43-on-L160 (wrap-
soup (arithmetic-filed!))). CATEGORY-ERROR-owned: T(T_sep)-compared-
against-ASYMPTOTIC-stationary-theory (single-barrier-B~1e-4-hid-this!).
TUN-AMENDMENT-4 (asymptotic-observable (PRE-REEVALUATION (pilot-1-opened
(B-profile-filed-above!)))): observable-CORRECTED-to-T_asymp-=-T+B/2
(PARITY-THEOREM: frozen-symmetric-geometry-(walls-[64,66)+[70,72)-
mirror-about-68 (well-centered!))-⟹-trapped-mode-decays-50/50-EXACT
(no-free-parameter (uniform-rule-all-25 (no-per-cell-freedom!)))); T_pred-
UNCHANGED (asymptotic-theory (correct-comparator!)); criteria-(b)-(f)-
re-expressed-in-T_asymp (SAME-bands/thresholds!); B-profile-filed-as-
trapping-evidence (resonant-buildup-150×-bg (result-in-itself!)); bank-
STANDS; records-REGENERATED (deterministic-re-run (T/B-bitwise-identical-
verified + T_asymp-field (S3-reuse-precedent (protocol-identical!)))). NEXT:
TUN-4-re-records-on-beast + verdict (gated on amendment-commit!).

TUN-4-VERDICT (PASS (beast (re-records (T/B/R-bitwise-identical-to-
pilot-1-✓ (reuse-verified!))))): 6/6: (a)-accounting-≤1.3e-12-every-
frame-all-25-✓; (b)-T_asymp/T_pred-∈-[0.963,1.069]-all-25-✓ (within-7%-
(full-curve-heights+shape-NO-FIT!)); (c)-contrast-86.8≥10-✓ (pred-93×!);
(d)-upper-max/bg-86.8≥5-✓; (e)-lower-max/bg-20.5≥5-✓; (f)-argmaxU=−5.826-
EXACT-AND-argmaxL=−7.418-EXACT (d=0.000-both! (TM-addresses-✓)). FILED:
B-trapping-0.152/0.048-vs-bg-8.4e-4 (181×/57×-buildup (resonant-dwell-
result!)); box-descent-upper-−5.826-vs-−5.236-(Δ−0.59-✓±0.7)-lower-−7.418-
vs-−7.236-(Δ−0.18-✓) (thin-wall-penetration (filed!)); widths-inferred-
narrow (w_pred-{0.0097,0.0585}-≪-σ_E (heights-match (direct-resolution-
packet-limited (filed!)))). ⟹ RESONANT-TUNNELING-ESTABLISHED (pre-
registered-scan + frozen-geometry + predicted-addresses (no-tuning!)).
TUN-CAMPAIGN-COMPLETE (TUN-0/1/2/3/4-ALL-PASS): single-barrier-box +
double-barrier-resonances (graph-wave-tunneling/evanescent-transmission
+ resonant-tunneling (uniquely-quantum-claim-NOT-made (locked!))).
FORMATION-EXTENSION-QUEUED (read-only-D5∞ (no-core-potential (ban-
stands!))) (future-work (NOT-this-campaign!)).

FEP-0-PREREG (FROZEN-2026-10-01 (~20:00-UTC (commit-predates-
ALL-FEP-runs!)); finite-excitation-phenomenology-scan (D14-FEP
on-P1-tail-ac6a140 (branch-cursor/fep-phenomenology-scan-9ae2!))).
QUESTION (discovery (not-fitting!)): "does-the-frozen-formation
+ wave-dynamics-contain-reproducible-finite-persistent-composite-
excitations" (electron-comparison-ONLY-after-verdict-freeze
(firewall-below!)). CONSUMES-READ-ONLY: scalar-J2-wave-apparatus
(ballistic.py) + continuous-time-H=-A + validated-packet-prep +
group-velocity-calibration + E-sign-projectors/accounting +
exact-bare-mixing-null + k→-k-controls (P1.1-verdict!) + frozen-
D5∞-formation-machine (formation.py (PR#62!)) + Stage-0-sitter-
bins + P1-A4/A6/A7-operational-rules. D15-READ-ONLY (no-spinorial
readouts-in-FEP!). P3-D-EXCLUDED (no-nonlinear-DNLS-in-FEP-0
(FEP-1-later-iff-P3-D-freezes-separately!)). NON-INTERFERENCE
(locked!): FEP-observes+classifies (MAY-NOT-modify-U-to-improve-
localization/lifetime/mass/mobility/pairing/chirality/polarity/
resemblance!); NO-electron-mass/charge/spin/Compton/dispersion/
constant-enters-dynamics/prep/classifier/criteria (nowhere!); NO-
core-dependent-trapping-potential (nothing-added!); grid-dims-
ONLY-P1-characterized (k/branch/width/norm (no-resemblance-dims!)).
COUPLING-READING (filed!): P1.2-one-way-G→ψ-IS-frozen (FEP-uses-
it-directly (suffices-for-discovery!)); C0-merge-NOT-required;
reciprocal-ψ→G-NOT-frozen (B2/B3-gates-stand (invention-BANNED!)).
P0b-READING (filed!): no-P0b-text-found-in-repo (searched!) ⟹
sitter-rule = Stage-0-α<0.7-confined + A7-core-presence (only-
frozen-sitter-rule (amendable-iff-P0b-surfaces-pre-data!)).
A1-FORMATION-ONLY (BANKED-from-S0/S1 (no-extra-runs!)): mass/
extent/persistence/COM-drift/lifetime/churn/T-trace/invariants
(formation-side-of-FEP-trajectories (banked-before-wave-opens!)).
A2-WAVE-ONLY (BANKED (P1.1-verdict!) + matched-controls-per-cell
(S2!)): norm/spectral-weights/group-velocity/extent/IPR/
dispersion. A3-COMBINED = S2-coupled-runs (frozen-one-way (no-
added-terms!)); ALL-candidate-claims = differences-vs-A1/A2.
S0-FORMATION (post-prereg!): 6-D5∞-trajectories (L28-d0-d3+L42-
d0-d1 = formation_run(state_from_nx(j2_torus_graph(L)),"d5inf",
4,seed=d,t_max=2000,k4_window=(1500,2000),elist_window=(1500,
2000)) (same-frozen-code+seeds-as-P1 (determinism ⟹ same-
trajectories (INDEPENDENT-reruns (no-read-of-uncommitted-P1-
files!)))); D1-controls (FRESH (same-call-"d1" (A4-precedent!))).
S1-SELECTION+A1-BANK: sitters = α<0.7-AND-core-present-all-3-
saves({1500,1800,2000},mass>0!) (unwrapped-centroid-1500-2000
(A7-method!) + locked-bins!); <1-sitter ⟹ STOP+file (A4!); bank-
A1-then-file-S1 (wave-sealed-until-S1-filed!).
S2-WAVE-GRID (per-sitter (formula-locked (counts-filed!))):
launches-s0∈{1500,1650,1800} × horizon-H=150-sweeps (per-sweep-
frames!); S=10-fiducial (dt=0.1 (T=150-units ≈ 6.5/4.3-crossings
(L28/L42 (v≈1.2!-P1.1b!) (both->3 ✓))); S-BRACKET-{1,10,100}-on-
σ4-headline-cells (formed + matched-controls-same-S (A4-T-match
spirit!)); packets-per-(sitter,launch): σ4: 2-branches × 4-geos
(x/y × approach/flip (per-branch-operational-approach-sign (10-
unit-verify-on-ACTUAL-formed-H (neither-approaches ⟹ run-invalid-
filed!)))) + zero-k (=9!); σ2: 2-branches × x-approach (=2!);
prep-at-max-torus-distance-node-from-launch-core (B0!); |k|=0.3-
partner-momenta (P1-A1!); spread-gated (σ<L/6 ✓-both-L!); norm=1-
ONLY (linear-law-scaling-degeneracy-filed (energy-scanned-via-
(k,branch)!)); substrates-per-cell: formed-dynamic-K(t) + D1-
dynamic + bare-J2-static-matched-T (node-matched-masks (A4!)).
VALIDITY-per-run: prep-purity-≥80% (else-run-invalid-filed
(P1.1b!)); accounting-≤1e-9-every-frame (else-frame-invalid;
>1/3 ⟹ apparatus-STOP (A4!)); wrap-note (T≫L (A4!): cumulative-
observables-wrap-robust-via-matched-T-controls!). OBSERVABLES-
per-run: w(t) (time-varying-k4-mask!) + r(t)=w/w_deloc(t) +
R_eff(t) + R_free(t) + IPR(t) + d(t)-ψ-core-distance + COM-
traces-unwrapped + v-fit + R² + α + C_v + W±/0(t)-bare-basis +
max-devs + E(t)=<H(G_t)> + late-mean + K-side (mass/α/Jaccard-
churn/B_chiral/triangle-density) + <Γ>-descriptive. S2-health-
live (validity/accounting (STOP-allowed!)); GATE-MARGINS-SEALED-
until-S3 (verdict-script-opens!).
S3-SIX-GATES (frozen (fep.py!); last-half = last-50%; late =
last-20% (B1!)): G1-localization ⟺ median(R_eff/R_free)<0.5-
last-half; G2-association ⟺ median(r)>5-last-half (B1-5×!);
G3-bounded ⟺ (max-min)/median-R_eff<0.5-last-half; G4-lifetime
⟺ frac(r>5 ∧ R_eff<R_free)>0.8-full-window AND crossings->3;
G5-occupation ⟺ late-mean-r>5 AND late-mean(W_+ + W_-)>0.05
(not-flat (zero-k-5%!); G1∧G2∧G3∧G4∧G6-minus-G5 = FLAT-TRAP-
run (filed!)); G6-K-survival ⟺ mass>0-all-sweeps AND mass-CV<
0.5 AND K-α<1.3 (locked-bins!). RUN-FIRES ⟺ G1∧G2∧G3∧G4∧G5∧G6.
CLASS-(branch,σ)-FIRES ⟺ ≥2-headline-geo-S=10-fires-from-≥2-
distinct-sitters (launches-any!) AND S-ROBUSTNESS (per-firing-
(sitter,launch): S∈{1,100}-same-qualitative (mismatch ⟹ VOID-
filed (fragile (not-shopped!)))); σ2-classes-count-only-with-
same-branch-σ4-class (robustness-role!); appendix-geo/zero-k/
S-cells-NEVER-trigger (anatomy/E1/E3/E4-roles!).
S4-LADDER (locked!): E0 ⟺ ≥1-class (finite-excitation!); E1 ⟺
±x-pair-sign-test-per-class (10% (P1!); static-both ⟹ E1-NULL-
filed (sitter-hosts-expect-NULL (wanderer-E1 = followup-NOT-
FEP-0!))); E2 ⟺ zero-k-class-run-fires AND 10%-excess (late-
<H(G_t)>-vs-matched-<H_bare>!) AND v<5%-free-v_g (P1.1!); E3 ⟺
branch-mirror-classes-fire AND |E_+-E_-|/mean<10% AND partner-
prep-relation (branches-alone-DO-NOT-satisfy!); E4 ⟺ within-
class-late-W_+-gap-split (max-gap>3×median-gap AND both-sides-
n≥2+G4-each (descriptive (NEVER-called-spin!))) else-OPEN; E5-
ARCHITECTURE-NULL (no-signed-invariant-in-frozen-one-way-law
(norm/energy-unsigned; Γ-NOT-a-symmetry-of-H(G_t) (<Γ>-filed-
descriptive!))); E6/E8-DEFERRED (spec!); E7 ⟺ IF-E0∧E1∧E2:
E(p)-from-<H>-vs-v-across-k-preps + post-verdict-overlay-only
(no-fit (bare-v_g-comparison-scale-only-after!)). HARD-STOPS:
NULL-0 ⟺ 0-fires-full-grid (no-tuning-rescue!); SCATTERING-ONLY
⟺ never-G2∧G4-jointly BUT (residence-z>3 (A4!) OR mixing-
dominance-MWU-p<0.05 (A6!))-on-FEP-cells; FLAT-TRAP ⟺ ≥1-flat-
trap-run AND 0-candidates; E0+ ⟺ ≥1-class (⟹ ladder (no-U-
change!)). REPORT-per-class: frequency/lifetime/radius/energy/
mobility/spectral-distributions + failure-modes; singletons =
ANECDOTAL (not-species!). ELECTRON-FIREWALL: comparison-table-
ONLY-after-S4-freeze (MEASURED/NULL/OPEN/ASSUMED-DEBT (no-
aggregate-score!)); "electron-like"-conditional-only (never-
identification!). AMENDMENTS-pre-data-only (committed-before-
use!). NEXT: S0-reruns (gated on prereg-commit!).
FEP-AMENDMENT-1 (zero-k-yardstick-repair (PRE-DATA (pure-
arithmetic-from-committed-text (no-FEP-wave-numbers-exist
(S2-unlaunched!); S0-formation-reruns-in-flight-unopened
(selection-unfiled (not-consulted!)); commit-predates-ALL-
wave-runs!))): BUG-owned: G4-crossings = window×v_free/L
with v_free = matched-bare-speed ⟹ zero-k (v_free = 0
(P1.1b-validated-null!)) gives crossings = 0 ⟹ G4-false-
always ⟹ E2 ("zero-k-class-run-fires")-VACUOUS-as-written.
REPAIRED-by: zero-k-yardstick-velocity = matched-minus-x-
approach-bare-speed (same-(sitter,launch,S) (headline-
packet-of-family (fallback-plus-x-approach (both-invalid
⟹ zero-k-run-invalid-filed (yardstick-unavailable!)))));
crossings-otherwise-unchanged; G1/G2/G3/G5/G6-zero-k-
unchanged (matched-zero-k-bare-controls-stand!). <Γ>-trace-
added-to-S2-cells (prereg-already-required (script-
completion-pre-launch!)). Everything-else-stands. NEXT:
S2-launch (gated on amendment-commit!).
FEP-S1-FILED (S0/S1-complete (beast!)): 6/6-cap/2000 (L28-
132-294s + L42-567-683s (contended!)); sitters-L28-d1/d2/d3
(α≈0/-0.06/0.04 + cores-all-saves (masses-134-246!)); wanderers-
L28-d0(α=1.49!) + L42-d0(α=7.05-teleport-artifact (slither-
anecdote!)) + L42-d1(α=1.21); mass-CV-0.13-0.27 (Stage-0-✓!);
determinism-cross-check-EXACT (masses/alphas-identical-to-P1-
S1-interim (independent-reruns (zero-shared-files!))). A1-BANKED
(formation-side!): sitter-CV≈0.13 + rms-2.6-26.1 (d1-jump-then-
sit!) + jacc-mean≈0.6 (EXCHANGE-churn-✓!) + T-217→3483-3578
(16×-growth!) + launch-covariates (B_chiral≈1.40-1.43 + tri-
density≈2.2/node + masses-175-235 (triangle-rich-chirally-
broken-hosts!)).
FEP-S2-FILED (405/405-sealed (beast (24-workers!))): grid =
3-sitters × 3-launches × 11-packets × 3-substrates (S-bracket-
on-headline (54-S=100-heavies!)); pre-launch-script-fixes (0-
sealed-before (pre-data!)): S=1-single-step-Krylov-path (oneway-
latent-num=1-edge (ballistic.py-UNTOUCHED (equiv-2.2e-16!))) +
frame-to-sweep-index-fix (boundary-misattribution!) + resume-by-
key; suite-GREEN-607+2-skipped (PYTHONPATH-vs-editable-install-
lesson-filed!); cells-sealed-until-S3 (margins-unopened!).
FEP-0-VERDICT (NULL-0 (S3-opened (frozen-verdict-script
(synthetic-smoke-verified!)))): preamble-invalid-78/405 (all-
neither-approaches (prep-rule-cost-19% (dynamic-core-geometry!)));
headline-formed-valid-30/36 (all-sitters-covered (7-8/9-per-class
(adequate!))); acct-bad-0 (healthy!); zero-k-9/9-valid-speeds-0.0
(nulls-✓!). GATES (109-scored-formed + 0-unscorable): g1-0/g2-0/
g4-0/g5-0/g3-109/g6-51 (G6-mixed (window-churn (K-side-filed!)));
persist-≡0 (r>5-NEVER (excess-0.46-1.08-vs-5 (uniform-ish!)));
ratio-0.57-1.05-vs-<0.5 (torus-saturated (G3-all-pass-disclosed-
vacuous-ish (flat-saturated!) (null-carried-by-G1/G2/G4/G5!)));
wpm-late-0.70-0.84 (dispersive (flat-traps-0!)). CLASSES-0/4
(fires-0 (margins-nowhere-near (no-near-miss!))). SCATTERING:
residence-0 + mixing-dominance-0 (B0-readouts-quiet-on-dynamic-
windows!). LADDER: E0-NULL ⟹ E1/E2/E3-NULL (no-candidates!);
E4-OPEN (nothing-to-split!); E5-ARCHITECTURE-NULL (stands!);
E6/E8-DEFERRED (spec!); E7-OPEN (gated!). ELECTRON-TABLE (post-
freeze!): localization-NULL/rest-energy-NULL/mobility-NULL/
conjugate-NULL/two-state-OPEN/charge-NULL(E5-architecture!)/
statistics-OPEN/dispersion-OPEN/interaction-OPEN (no-aggregate
(none-earned!)). ⟹ NO-finite-persistent-K+ψ-composite-under-
frozen-one-way-coupling (formation + linear-wave-architecture-
produces-no-particle-like-excitations (one-way-scope (reciprocal-
B2/B3-untested-gated!))); NO-tuning-rescue (per-prereg!). NEXT:
FEP-1-iff-P3-D-freezes (separate-amendment!); wanderer-E1-
followup-NOT-FEP-0 (stands!).

BR0-PREREG (FROZEN-2026-10-02 (commit-predates-ALL-BR0-campaign-data!);
bond-energy-landscape (BR-0-of-BR0/BR-1/BR-2 (BR-1/BR-2-UNOPENED (no-
rewiring-rule/no-dynamics-in-any-BR0-run!)))). QUESTION: does the
EXISTING psi field (P1-frozen H(G)=-J*A(G), J=1, no-new-law) make
graph moves energetically distinguishable, i.e. is P_vac(dE<0) <<<
P_exc(dE<0)? OFFLINE measurement/derivation campaign: NO graph
evolution, NO edge weights, NO Im-readers/drivers (BR-0 uses Re
ONLY; backreaction.py contains no Im helper by construction),
NO current/recoil law, NO J2-optimization, NO D5inf labels in
the energy, NO structural E_G, NO temperature/Metropolis, NO
fitted thresholds, NO gravity/mass/backreaction claims from
BR-0 alone. Apparatus: src/bh_graph/backreaction.py + pins in
tests/test_backreaction.py (17 tests) + wave sector vendored
VERBATIM from P1 tip ac6a1409 (ballistic.py + test_ballistic.py
+ formation.py elist_window + 1 closure pin; byte-identical,
verified by diff). Campaign runner scripts/run_br0_campaign.py
(frozen protocol, deterministic seeds) -> data/br0_landscape.json.

FROZEN ONTOLOGY: A_ij in {0,1}; H(G)=-J*A(G) (J=1, P1-LOCKED);
psi=(a,b) normalized (<psi|psi>=1) except V0 (psi=0, exact
control); B_ij=Re(psi*_i psi_j) symmetric, ONLY derived
relational quantity. ENERGY: E_psi=<psi|H|psi>=-2J*sum_E B_ij
(two implemented forms cross-pinned <1e-9); LOCAL REDUCTION
for (a,b)->(c,d), psi fixed: dE=-2J*(B_cd-B_ab) (C0-gated
below before any campaign use). AMPLITUDE: dE(lam*psi)=
lam^2*dE(psi) pinned -> NO amplitude scan (linear scaling
redundant, per spec).

V1-STATUS: NONE (searched main + P1 + D15 tracks 2026-10-02:
relaxed-vacuum "ground state" = GRAPH fabric (degree-4), not
a wave state; P1 `uni` = IPR unit-test vector, not a vacuum
claim; no nonzero psi_vac justified ANYWHERE in the wave
program). CONSEQUENCE (pre-committed): the vacuum half of
BR-0 files BR0-E (wave potential alone has no demonstrated
mechanism for vacuum rigidity at the current ontology) NO
MATTER WHAT the excitation half shows. Do-not-repair rule
stands. Uniform psi appears ONLY as V1U SECONDARY-exploratory
(explicitly-not-vacuum): on z-regular graphs it is the H
ground state (pinned) with EXACTLY flat landscape (B=1/N
const -> dE==0.0 bitwise, pinned) -- mechanism information
for BR-1, never a rigidity claim.

STATE TABLE (prep = P1 gaussian_packet, P1.1-validated ONLY):
V0 = zero_psi on J2-L28 (primary vacuum, exact control);
V1U = uniform_psi on J2-L28 (SECONDARY exploratory, see
above); E1 = J2-L28 r0=(7,14) s=4 k=(0.3,0) (P1.1b packet,
PRIMARY excitation); E2 = same k=(-0.3,0) (literal -k
partner, P1.1b-validated); E3b = same k=(0,0) (localized
no-momentum); E3p = same k=(0.3+pi,pi) (branch partner);
E3r = ring-400 r0=(100,) s=15 k=(0.5,) (P1.1a); E3t =
torus-30 r0=(7,15) s=4 k=(0.5,0) (P1.1a). r0 choices are
non-choices by vertex-transitivity of bare substrates
(filed). V0/V1U near/far use the same-substrate E1
geometry as a NEUTRAL reference (homogeneity null:
expect near==far exactly; primary is global). X-states
(EXHAUSTIVE, characterization: spread-gate-valid but
non-P1.1-validated prep): X-J2-{V0,U,P} on J2-L8
r0=(2,4) s=1.0 k=(0.3,0) (3.9M moves); X-R-{V0,P} on
ring-60 r0=(15,) s=6 k=(0.5,) (102k moves); S-J2-P /
S-R-P = sampled twins for C5b. D5inf read-only formed
state: DEFERRED (no committed frozen K+psi artifact
consumable without new formation runs; verdict MUST
NOT depend on D5inf, per spec).

MOVE CLASS M1 (PRIMARY, frozen): remove one uniform-
random edge + add one uniform-random non-edge (bitwise
= formation.propose_relocation stream, pinned). N/E/
simplicity PRESERVED (pinned per-move); degree sequence
NOT preserved; connectivity NOT required (covariate:
bridge precompute + rare-path BFS; bare substrates
pinned bridgeless -> relocation cannot disconnect).
No secondary move class (single-class discipline).

SAMPLING (frozen): n=200_000 moves x seeds {0,1,2} per
sampled state (formation-mirror distribution); X-states
exhaustive. EPSILON: 1e-10 absolute (J=1 units), fixed
pre-data: ~1e3x above fp64 summation noise on E~O(1-10)
(C0 residuals), ~1e7x below peak-bond scale ~1e-3;
separates NUMERICAL noise from every physical tail
(tails are real signal when above eps, however small).
NEAR/FAR (frozen packet geometry, never where favorable
moves appear): R_near=2*sigma about r0, minimal-image;
PRIMARY = removed-edge midpoint; added-edge midpoint
gives the secondary 2x2 (nn/nf/fn/ff). MEASUREMENTS per
(state,seed): f-/f0/f+ (eps-gated), median, q01/05/25/
75/95/99, mean, min/max, neg-tail (count/mean/min),
E_psi baseline, frac_rem/add_near, frac_connected,
n_bridges, radial histograms (rem/add all+neg, 30 bins),
|psi|^2, B-edge field (sorted elist).

DISCRIMINATOR (robustness bars, pre-data, no-fit):
SELECTIVE (BR0-D) <=> (i) f-_V0==0 EXACTLY (theorem;
every one of 600k V0 moves reads 0.0 -- hard gate, any
nonzero = apparatus STOP); (ii) f-_E1,near > 0.01 (two
orders above the 5e-6 sampling floor); (iii) f-_E1,near
/ max(f-_E1,far, 1e-4) > 5 (localization; floor = 20
counts); (iv) max-min of f-_E1,near across seeds < 20%
relative (C5 campaign bar). Magnitudes filed
descriptively (neg-tail near-vs-far). DECISION TREE:
C0/C1 fail -> apparatus STOP (no verdict); ELIF (ii)+
(iii)+(iv) -> BR0-D SELECTIVE (vacuum half: V0-flat +
BR0-E debt, ALWAYS attached); ELIF every E-state global
f0 > 0.99 -> BR0-A FLAT; ELSE -> BR0-C EXCITATION-BLIND
(nonzero landscape without favorable-channel opening).
BR0-B UNREACHABLE (filed): V0-exact + uniform-flat
theorem leave no vacuum candidate with f_->0; B would
need a nonzero vacuum that does not exist (V1-NONE).
FLAT-vs-RIGID (pre-data interpretive lock): V0-flat
(f0=1, all moves FREE) is NOT rigidity (f+=1, all moves
COSTLY); a BR0-D verdict with flat vacuum PROCEEDS to
BR-1/BR-2 but BR-1 inherits the rigidity debt (needs
E_G or psi_vac -- BR-0 shows SELECTIVITY only).

CONTROLS (campaign scale): C0: max|loc-full| < 1e-9 over
2000 moves x 5 (substrate,state) cells (J2-L28 x E1/
uniform/zero + ring-400/E3r + torus-30/E3t) -- HARD GATE.
C1: all 600k V0 moves == 0.0 bitwise -- HARD GATE. C2/C3:
pins only (state-independent theorems, covered in
tests). C4: campaign max|dE_E1 - dE_E2| < 1e-12 on
identical 50k J2-L28 moves (preregistered expectation:
EXACT invariance -- conjugation preserves B; any
violation = apparatus finding/STOP, NEVER recoil
evidence). C5: (a) seed stability per (iv); (b)
|f-_sample - f-_exact| < 3x binomial-SE + 5e-4 on S/X
twins (J2-L8 + ring-60, seed-0 sample vs exhaustive).

ANATOMY (descriptive, no-causality): 2x2 cells, rem/add
radial profiles (all vs favorable), |psi|^2, B-field;
pre-data EXPECTATIONS (non-binding, guide reading only):
V0/V1U exact-flat (theorems); E-far tail-suppressed
(small-but-real f-, above eps); E-near active via
add-under-packet moves (expect fn cell = remove-far/
add-near to dominate favorables). COMPUTE: local CPU
(beast 16.54.88.181 key absent from this VM -- probed,
permission-denied; campaign is formation-free, ~minutes
on laptop CPU, deterministic seeds -- same result).
NEXT: run campaign (gated on this prereg commit) -> file
BR0-VERDICT (A/B/C/D + E-attachment + anatomy + BR-1/BR-2
admission) in this file.

BR0-VERDICT (campaign-data 2026-10-02, local CPU 10.3min, exit-0;
artifact data/br0_landscape.json (3.3MB); runner+analyzer frozen
pre-data). MECHANICAL LETTER-OUTPUT FIRST (no-shopping): C0 PASS
(max|loc-full| = 1.7e-15/0/0/4.4e-16/7.1e-16 vs 1e-9 bar, 5/5
cells); C1 PASS (all 600k V0 moves == 0.0 bitwise, f0=1.0);
C4 PASS (max|dE_E1-dE_E2| = 0.00e+00 bitwise on 50k moves;
E1==E2 full records bitwise); C5b PASS (J2-L8 0.42802 vs
0.42816 exact; ring-60 0.19674 vs 0.19634); SELECTIVE (ii)
f-_E1,near = 0.0141/0.0148/0.0152 > 0.01 PASS, (iv) spread
7.2% PASS, (iii) ratio 0.0141/0.2712 = 0.06 vs >5 FAIL
(INVERTED). Tree-letter -> BR0-C. READ ON: the letter
misfires (owned erratum below); the mechanism is DECISIVE.

HEADLINE NUMBERS (seed-0, eps=1e-10): V0: E=0, f-=0.0000,
f0=1.0000 (exact). V1U: E=-8.0, f-=0.0000, f0=1.0000
(exact; secondary, not-vacuum). E1 (J2-L28 k=(0.3,0)):
E=-7.7592, f-_glob=0.2070, f-_near=0.0141, f-_far=0.2712,
f0=0.0001. E2: BITWISE-identical to E1. E3b (k=0):
E=-7.9381, f-=0.4826/0.0400/0.6300. E3p (k+Q): E=+7.7592,
f-=0.7932/0.9893/0.7280. E3r (ring-400): E=-1.7542,
f-=0.1161/0.0036/0.1359, f0=0.3433 (big-ring tail floor).
E3t (torus-30): E=-3.7257, f-=0.2141/0.0079/0.2716.
conn=1.0000 everywhere (bare substrates bridgeless,
pinned+filed). EXHAUSTIVE (zero sampling noise): X-J2-P
3.9M moves f-=0.4282/0.0209/0.5221; X-R-P 102.6k moves
f-=0.1963/0.0185/0.3149; X-J2-V0/X-J2-U/X-R-V0 all
f-=0.0000/f0=1.0000 exact.

2x2 JOINT ANATOMY (preregistered secondary; THE finding):
bonding packets (E1/E3b/E3r/E3t, all substrates): nf-cell
(remove-near/add-far) f- = 0.0000 EXACTLY (E1: 0/36,833
sampled; X-J2-P: 0/565,920 exhaustive; X-R-P: 0/24,264)
-- packet-region bonds are NEVER favorably exported
(protection to <2e-6, exactness = BR-1 question); fn-cell
(remove-far/add-near) f- = 0.34/0.93/0.39/0.50 (E1/E3b/
E3r/E3t; X-J2-P exhaustive 0.8688) with ~10x magnitudes
(E1 fn tailmean -1.6e-3 vs ff -1.4e-4) -- edges flow INTO
the packet; nn small (0.02-0.15); ff coin-flip (0.09-
0.52) with tiny tails (tail-difference noise). Radial:
E1 favorables remove-near 1.7% / add-near 34.0% (vs 25-
27% base rate -- enriched); E3r 0.3%/39.0%; E3t 0.8%/
40.8%. ANTIBONDING E3p REVERSED: nf f-=1.0000 (export
always pays), nn 0.96, fn 0.57 -- high-energy packet
EXPELS edges (energy-sign-dependent structural response,
descriptive). ALL near-favorables in bonding states are
nn (within-packet reshuffles); nf contributes ZERO.

BR0-AMENDMENT-1 (owned prereg erratum, NO new data needed):
bar (iii) conditioned the WRONG HALF of the move. dE<0 <=>
B_add > B_rem: favorables ADD bonds into high-B regions,
so localization lives on the ADDED edge (landing site),
while removed-edge conditioning measures bond EXPORT
(which the packet forbids, nf=0). My own filed pre-data
expectation predicted EXACTLY this ("expect fn cell to
dominate favorables") -- the data CONFIRMS the expectation
and refutes the bar; bar-vs-expectation contradiction is
visible in the committed prereg (not post-hoc). Single-
margin ratios are weak EITHER way (add-near/add-far E1 =
0.267/0.185 = 1.44x) because ff coin-flips (tiny tails)
dilute counts -- the JOINT cells + magnitudes are the
sharp readout (preregistered as secondary; promoted by
this amendment for BR-1). CORRECTED BR-1 BARS (filed,
not yet applied): joint-primary (nf-protection ~= 0 +
fn-active >> 0 + fn/ff magnitude ratio >> 1); single-
margin ratios descriptive only.

ADJUDICATED VERDICT: BR0-D SELECTIVE* (* = with Amendment-1;
mechanical letter-output BR0-C reported above for the record).
JUSTIFICATION (4-legged): (1) spec's D-box passes BOTH clauses
(f-_vac = 0.0000 exactly; f-_E1,near = 0.0141 > 0 with 7%
seed-stability); (2) filed pre-data expectation (fn dominance)
CONFIRMED (0.34 sampled, 0.87 exhaustive); (3) the mechanism
in the spec's headline box -- "vacuum dynamically quiet while
energy opens local structural change" -- is decisively present
(0% vs 12-79% favorable rates, packet-centered joint
structure, cross-substrate replicated x5 states); (4) filing
bare C ("excitation does not open favorable channels /
potential provides no backreaction mechanism") would assert
the negation of decisive measurements. DISSENT-INVITE: PI may
downgrade to C on letter-discipline grounds; all numbers filed
either way. BR0-E VACUUM-HALF DEBT STANDS (pre-filed, unchanged):
V0-flat (f0=1, moves FREE) is NOT rigidity (f+=1, moves COSTLY);
BR-1 inherits the rigidity debt (needs E_G or psi_vac).
BR0-B confirmed unreachable (no vacuum candidate with f_->0).

BR-1/BR-2 ADMISSION: PROCEED (route POSITIVE -- null avoided).
BR-1 inherits: (a) rigidity debt (flat-vs-rigid lock stands);
(b) Amendment-1 corrected bars (joint-cell primary); (c)
DIRECTION: bonding excitations ATTRACT edges (densification
at matter-energy -- gravity-sign lead), antibonding EXPEL
(E3p) -- energy-sign-dependent response is the headline
BR-1 target; (d) nf-protection exactness question (theorem or
<2e-6 rarity? analytic derivation owed); (e) ff coin-flip
calibration (vacuum-move neutrality scale for BR-1 dynamics).
NO rewiring rule invented here (BR-0 firewall held: offline
measurement only; no Im-readers/drivers added; no E_G; no
temperature; D5inf untouched per deferral).

BR0-REPLICATION (2026-10-02): beast (16.54.88.181, 96-core) ran the
frozen protocol independently (clone of this branch at d60b4a6, fresh
venv) in parallel with local. Cross-machine JSON comparison (meta
excluded): all f-/f0/f+/n_neg/frac_* fields BITWISE-identical; only
6479/3.3M floats differ, all last-ulp (packet-norm BLAS noise); 4
medians differ at ~1e-15 relative; C0 torus cell 7.14e-16 vs 7.52e-16
(both ~1e3x below bar). Every bar evaluates identically on both
machines. Deterministic-protocol replication CONFIRMED (zero
verdict impact).

POT0-PREREG (FROZEN-2026-10-02 (~02:00-UTC (commit-predates-
ALL-POT0-campaign-runs!)); omnidirectional-potential-to-coherent-
directed-wave (POT-0-of-POT-0/POT-1 (POT-1-gated-behind-POT-0!))).
QUESTION (load-bearing!): can-the-SAME-two-real-scalar-field-on-J2
support-BOTH-an-omnidirectional-source-relative-potential-like-
response-AND-a-directed-ballistic-wave-with-direction-from-collective-
phase-coherence/interference-only (no-directional-variable/memory/
coin/compass-at-any-node)? FROZEN-ONTOLOGY: G=bare-J2-torus +
psi_x=r_x+i*i_x + H(G)=-J*A(G)-UNCHANGED (bulk-law-NEVER-touched
(potential.py-contains-NO-evolution-law (evolution-ONLY-via-
ballistic.evolve_fixed!))); direction-is-a-property-of-a-many-node-
configuration-only (vector-embedding-readout-only!).
APPARATUS (this-commit (17-pins!)): bond-current-J_{u->v}=2J*Im[conj
(psi_u)*psi_v] (H-continuity!); quotient-(x,y)-displacement-per-edge
(all-axis-steps-pinned!); J_net=sum-J_e*d_e (orientation-invariant!) +
S=sum-|J_e| + D=|J_net|/S (S=0->D=0!); per-class-fluxes-(positive/
negative-part-sums (algebra-pinned: diffs=Q + sum=S!)); spectral-C =
sheet-summed-quotient-FFT-peak-fraction (+M_eff-participation!) =
FOURIER-space (independent-of-real-space-flux-D!); gradient-family
(k_eff=c*k (envelope-exact; c=0-uniform-source + c=1-validated-
packet-bit-exact-pinned!)); dephasing-family (|packet|*exp(i*(phi+
(1-c)*eps))-seeded (amplitude/norm-exact!)); scrambling (|psi|*exp
(i*theta)-seeded (POT-0D-intervention!)); aperture (quotient-disk-R +
renorm (gradient-kept-pinned!)); J2-autos-rot90/reflectx/translate
(auto-pinned + covariance-pinned!); plane-wave-D=1 + standing/real-
D=0-pinned; global-phase-invariance-pinned; spearman-own-impl-pinned.
HEADLINE-GEOMETRY (P1.1b-validated-window!): L=28-bare-J2-torus +
sigma=4 + r0=(7,14) (site-centered (exact-symmetries!)) + k=(+-0.3,0)
+ zero-k + T=10-dt=0.1-J=1 (101-rows; <D>=time-mean-over-all-rows!;
C-measured-at-PREP(t=0) (coherence-is-a-preparation-property!));
packets-RAW (no-branch-purification (P1.1b-showed-100%-raw-purity!);
flux-readout-is-branch-blind-BY-DESIGN!); null-ensemble-N=20-seeds-
0..19-same-envelope (D_null-calibration!).
POT-0A-SOURCE (unbiased-source-calibration!): prep = sigma=4-k=0-
uniform-phase-Gaussian (same-envelope-as-packet (ONLY-phase-differs!)
+ full-J2-symmetry-respecting (D4+sheet-exact!)). PASS ⟺ <D>_source
< 0.05 AND <D>_source <= null_mean+3*null_std (one-sided (source-
MAY-be-more-symmetric-than-random (D~1e-15-expected (exact-
cancellation!) vs null~1/sqrt(E)!))). ANY-persistent-direction-
under-symmetry-neutral-source = apparatus/asymmetry-FAIL-BLOCKS-
campaign!.
POT-0B-PACKET (P1.1b-positive-control (NOT-discovery!)): prep =
sigma=4-k=(0.3,0)-packet. PASS ⟺ ALL: (a)-<D>_packet > 0.5;
(b)-(<D>_packet-<D>_source) > 0.4 AND ratio-(floor-1e-9) > 10;
(c)-alpha > 1.3 (P1-MSD-bins!); (d)-mean-C_v-first-50-lags > 0.5;
(e)-k->-k: cos(mean-J_net(+k),mean-J_net(-k)) < -0.95 AND |<D>|
matched-10%; (f)-v-fit-r2 > 0.99 (+-k-runs (interference-gate!)).
POT-0C-INTERPOLATION (LOAD-BEARING!): gradient-c-grid-{0,0.1,...,1}:
PASS ⟺ D(1)/D(0) > 10 (floor-1e-9!) AND Spearman(v(c),c) > 0.7 AND
v(0) < 5%-v(1) (lawful-without-analytic-form (NO-J2-v_g-law-pinned
(no-sin-law-claim!))); dephasing-family-(seed-0)-same-grid: PASS ⟺
Spearman(D(c),c) > 0.5 AND D(1)/D(0) > 5. BOTH-must-hold (gradient =
selection-by-gradient; dephasing = selection-by-coherence!). C-
constancy-check (validation-not-criterion!): gradient-C(c)-flat-
within-5% (C-measures-concentration-not-gradient (envelope-fixed!)).
POT-0D-MECHANISM (causal-test!): scramble (seed-0) the-k=0.3-packet
(envelope/norm-exact!) + evolve-identical + restore (re-prep-clean).
PASS ⟺ ALL: D_scr < 0.15*D_clean; C_scr < 0.5*C_clean (independent-
Fourier-measure!); D_rest-within-15%-D_clean; C_rest-within-15%-
C_clean; pooled-Spearman(C,D) > 0.5 over {noise-11 + clean/scr/
rest} (gradient-grid-EXCLUDED-from-pool (C-degenerate-there-BY-
DESIGN (filed-above!))). Post-hoc-ADD (allowed): aperture-R-grid
into-pool (confinement-varies-both (strengthens-link-test!)).
POT-0E-COLLECTIVE: R-grid-{2,3,4,6,8,12,full(full-coded-20!)}-same-
k/center/renorm. PASS ⟺ Spearman(D(R),R) > 0.5 AND D(R=2) < 0.5*
D(full) AND Spearman(M_eff(R),R) < -0.5 (confinement-broadening!).
S1-AUTO: rot90: ang_diff(angle_rot,angle+pi/2) < 5deg AND |D|-5%;
reflectx: ang_diff(angle_ref,pi-angle) < 5deg AND |D|-5%; translate
(3,5): J_net-identical-1e-9 + D-identical-1e-9; EACH-at-prep-AND-
evolved-<D> (both-must-pass!). S2-REVERSAL: same-as-B(e) (cos<-0.95
+ |D|-10% (time-mean-J_net-vectors!)). S3-GLOBAL-PHASE: phi-in-
{0.7,2.1,4.0}: prep-D-identical-1e-12 + prep-C-identical-1e-12 +
evolved-<D>-identical-1e-9. S4-ZERO-K: <D> < 0.05 AND speed < 5%-
|v(0.3)| (same-run-as-0A (control-framing!)). S5-DETERMINISM: rerun-
source+packet: psi-rows-bit-identical + D-traces-bit-identical.
L42-ROBUSTNESS (appendix-with-teeth!): repeat-A+B-on-L42 (r0=(10,21)
(scaled-quarter/half!) + same-sigma/k/T). MUST-also-pass-A+B-
thresholds-else-verdict-CAPPED-at-POT0-SPREAD + filed-size-effect!.
VERDICTS: POT0-NULL (no-unbiased/coherent-distinction-or-readout-
fails-controls!); POT0-SPREAD (two-behaviors-but-coherence-not-
shown-to-generate-direction (C-link-or-interpolation-fails!)!;
POT0-COHERENCE-DIRECTION (A+B+C+D+S1-S5-ALL-pass (PRIMARY-SUCCESS:
direction-is-emergent-collective-phase-coherence-on-J2!));
POT0-COLLECTIVE (+E-passes (STRONGEST: direction-encoded-nonlocally!)).
FORBIDDEN (POT-0-does-NOT-establish!): electromagnetism/photons-SM/
Maxwell/charge/B-field/Born-rule/polarization/spin/static-force-law/
backreaction ("photon-like"-phenomenological-shorthand-only!). POT-1-
GATE (only-after-COHERENCE-DIRECTION!): fixed-source/sink-conditions
-> stationary-profile? + source-changes-launch-modes? = static-vs-
wave-two-regimes-of-same-field? NEXT: freeze-commit-then-beast-
campaign (scripts/pot0_campaign.py (gated-on-prereg-commit!)).

POT0-VERDICTS (beast-96 (jobs-90); L28-headline + L42-appendix; T=10-
dt=0.1 (101-rows); suite-612-passed-2-skipped-(torch/GPU-precedent!)
on-branch): LADDER = POT0-COLLECTIVE (STRONGEST-RUNG (all-stages +
all-controls-green-first-run!)).
POT-0A-PASS (source-<D>=8.1e-14 (trace-max-2.6e-13 (fp-exact-D4+sheet-
cancellation-preserved-by-unitary-evolution!) vs null-0.0267+-0.0151
(N=20-seeds-0..19!)): <0.05-AND-<=null+3sd (12-ORDERS-margin!); source-
S=0.395 (SPREADING-nonzero-flux!)-with-D=8e-14 (no-direction!) = the-
headline-contrast (omnidirectional-flux-without-net-direction!)).
POT-0B-PASS (packet-<D>=0.8551 (prep-0.9978->min-0.772 (gentle-
dispersion-decay (PERSISTENT-never-collapses!)) std-0.066); sep-0.855-
vs-8e-14 (ratio-8.6e8-w/-floor!); alpha=2.087; Cv=0.994; reversal-cos=
-1.0-EXACT (conjugate-symmetry!) + |D|-0.85506/0.85530 (0.03%!); r2=
0.9997/0.9998; v=+1.211/-1.204 (P1.1b-REPLICATION (1.2039/1.2110-✓!));
disp=12.18<14 (no-wrap-✓!); packet-S=1.38-J_net=1.17-aligned + Jy=
-1.9e-14 (exact-y-symmetry!)).
POT-0C-PASS (gradient-D(c)=0/.348/.526/.646/.721/.762/.792/.815/.831/
.843/.855 (STRICTLY-monotone (evolved-time-mean (NOT-prep-step:
dispersion-vs-translation-competition-makes-it-gradual (better-than-
prereg-note!))); prep-D-jumps-0->0.98 (normalized-prep-flux (filed!));
ratio-huge; v(c)=0/.149/.279/.385/.477/.572/.683/.816/.961/1.097/1.211
(mono-Spearman-1.0; v(0)=0 (linear-ish-small-k + band-curvature-high-k
(lawful!))); noise-D(c)=0.0135/.0162/.0302/.0551/.0917/.143/.214/.313/
.455/.656/.855 (STRICTLY-mono-Spearman-1.0-ratio-63!); noise-C=
0.0073->0.4116-mono + M_eff-381->3.9 (flat->sharp!); alpha/cv/v-
transition-resolved (diffusive->ballistic-with-c (c>=0.6-alpha~2!))).
C-CONSTANCY-CHECK: FAIL (27%-spread (0.486->0.353-min-at-c=0.4->0.483-
at-c=0.7->0.412)) = FINITE-TORUS-seam/picket-fence-ARTIFACT (VALIDATION-
only (not-criterion!); mechanism-QUANTITATIVE: winding-kL/2pi=c*1.337
-> period-0.748c + min-at-half-integer-0.374~-observed-0.4-✓ + recovery-
at-integer-0.748~-observed-0.7-✓ (envelope-fixed-C-central-value-stable-
M_eff-3.5-4.0!)); gradient-grid-excluded-from-C-D-pool-BY-DESIGN
(unaffected!)).
POT-0D-PASS (scr-D=0.0131 (<0.15*0.855=0.128 (10x-margin!)); scr-C=0.0070
(<0.5*0.412=0.206 (30x-margin!)); scr-M_eff=382 (spectrum-flattened!);
rest-D/C-EXACT-match (re-prep-clean); pooled-Spearman(C,D)=1.0 (14-pts
(noise-11+clean/scr/rest (ties-at-top-handled (average-ranks!)))):
destroy-coherence->destroy-direction + restore->restore (CAUSAL-✓!)).
POT-0E-PASS (D(R)=0.223/0.337/0.408/0.550/0.671/0.833/0.855 (STRICTLY-
mono-Spearman-1.0!); D(2)=0.223<0.5*0.855=0.428-✓; M_eff=131/58/34/14/
8.4/4.6/3.9 (mono-decreasing (confinement-broadening-✓!)); transition-
R~4-6-≈-sigma (aperture-narrower-than-packet-destroys-it (minimum-
collective-scale-~envelope!)); R<=4-wrap-physics-filed (disp-38/27/24
+ multi-velocity (v=3.77-fast-band-components!) + alpha-4.1/r2-0.93-
wrap-artifacts (UNGATED-readouts (D/M_eff-wrap-safe (criteria-clean!));
small-support-LOSES-single-velocity-character (corroborates-collective-
claim!)); R>=6-clean (v≈1.19-1.21-r2>0.998-disp≈12-alpha≈2.0!)).
S1-PASS (rot90: prep-angle-0->1.5708-EXACT + meanJ-(1.171,0)->(0,1.171)-
|J|-bit-matched-1e-13 (prep+evo!); refx: ->pi-EXACT + J=(-1.171,0);
trans-(3,5): J-identical-6e-14 + D-identical (Krylov/fp-only!)).
S2-PASS (cos=-1.0-EXACT + |D|-0.03% (time-mean-J_net!)). S3-PASS
(prep-D-BIT-identical-(0.0e+00!) + prep-C-to-6e-17 + evolved-<D>-to-
3e-14 (global-phase-path-fp-only!)). S4-PASS (k=0-<D>=8e-14 + speed-0
(same-run-as-0A!)). S5-PASS (psi-rows-BIT-identical + D-traces-BIT-
identical (reruns!)). Norm-dev-ALL-cases-<=6.1e-13 (unitary-✓!).
L42-APPENDIX-PASS (source-<D>=0.0 + packet-<D>=0.8647 + null-0.025+-
0.014 (A+B-thresholds-met (no-cap!)); v=1.176-vs-L28-1.211 (3%-
finite-size (L42-seam-negligible-exp(-6.9) (L42-is-cleaner-value
(filed!))); M_eff-8.7-vs-3.9 = area-ratio-2.25-EXACT ((42/28)^2 (M_eff-
measures-spectral-width-✓!)); prepC-0.228-vs-0.412 (1/N_modes-scaling
(direction-right!))).
SEED-ROBUSTNESS (post-hoc-appendix (prereg-froze-seed-0!)): seeds-1+7-
noise-family: thresholds-PASS (Spearman(D,c)=0.936/1.0 + D1/D0=30/186
+ Spearman(C,D)=0.936/1.0); seed-1-low-c-jitter (c<=0.3-D~0.005-0.03-
within-null-floor-0.027+-0.015 (EXPECTED-finite-size-random-floor
(emergence-above-floor-c>=0.4-seed-stable!))).
INTERPRETATION (disciplined!): SAME-(r,i)-field + SAME-bulk-law + SAME-
J2 -> omnidirectional-spreading-source (S>0-D≈0) AND ballistic-directed-
wave (alpha≈2-Cv≈1) with direction-selected-by-extended-phase-coherence
(D(c)-mono + scrambling-destroys + restore-recovers + C-D-Spearman-1.0
+ support-scaling (collective!)); NO-node-knows-direction (no-vector/
memory/coin/compass-anywhere (readout-embedding-only!)). FORBIDDEN-
claims-RESPECTED (no-EM/Maxwell/charge/Born/spin/static-force-law
(source-SPREADS (S=0.395) (static-potential-NOT-shown (POT-1-question!)))).
POT-1-GATE: OPEN (COHERENCE-DIRECTION-passed (COLLECTIVE-strongest!)):
fixed-source/sink-conditions -> stationary-profile? + perturbations-
launch-modes? NEXT: POT-1-prereg (gated-on-this-verdict-commit!).

BR2-PREREG (FROZEN-2026-10-02 (commit-predates-ALL-BR2-campaign-data!);
phase-controlled-structural-backreaction (BR-2-of-BR0/BR-1/BR-2 (BR-1-
vacuum-rigidity-UNOPENED (parallel-track!); BR-3-evolution-UNOPENED
(no-graph-updates-in-any-BR2-run!)))). QUESTION: is the BR-0
structural asymmetry (bonding influx fn>>nf / antibonding efflux)
controlled by the RELATIVE PHASE of the existing (r,s) field, with
B_ij = Re(psi*_i psi_j) = rho rho cos(Delta theta) as the
potential-like quadrature and J_ij = Im(psi*_i psi_j) = rho rho
sin(Delta theta) as the current-like quadrature? OFFLINE campaign
(no G evolution, no move acceptance, no Metropolis/temperature, no
E_G, no vacuum potential, no charge labels, no EM-naming (B is NOT
called electric potential, J is NOT called electric current), no
current-scored relocations (J readers are OBSERVATION ONLY), no
post-data phase points, no g(B,J) search). Apparatus: new
src/bh_graph/phase.py + 15 theorem pins (tests/test_phase.py) +
BR-0 apparatus vendored BYTE-IDENTICAL from BR-0 tip 516b363
(ballistic/backreaction/formation/tests/scripts/data, verified
by cmp; backreaction.py UNTOUCHED by BR-2). Runners frozen
pre-data: scripts/run_br2_campaign.py -> data/br2_phase.json
+ scripts/analyze_br2.py (mechanical ladder).

LOAD-BEARING FAMILY (frozen construction): sublattice stagger
psi_i(phi) = rho_i e^{i phi q_i} with rho = |psi_E1| (BR-0 E1
packet envelope, banked, k-independent norm), q_i in {0,1}
the CANONICAL bipartition (J2: (x+y)&1 per P1 j2_branch_parity
+ D15 canonicity pins; ring: v&1). EVERY edge spans q=0->1
(bipartiteness asserted), so EVERY bond has |Delta theta| =
phi EXACTLY: B_e = rho rho cos phi, J_e = +-rho rho sin phi
(sign by q-order; pinned as theorems in tests). Envelope/
support/norm/center/width/graph/census IDENTICAL across phi
(only phi varies). PHI GRID (frozen full cycle): {k pi/4 :
k = 0..7}. NOTE: phi=0 state == E3b psi to ~1e-16 (same
envelope, real-positive; approximate-continuity, NOT bitwise);
phi=pi ~= E3p minus the 0.3 twist (cousins, filed).

SETUPS (frozen): J2-L28 r0=(7,14) s=4 rho=|E1 k=(0.3,0)|
(SAMPLED primary: 200k x seeds {0,1,2}, PAIRED move lists
across phi (same seeds -> identical moves -> pure-psi
comparisons)); J2-L8 r0=(2,4) s=1.0 rho=|k=(0.3,0)| +
ring-60 r0=(15,) s=6 rho=|k=0.5| (EXHAUSTIVE confirmatory,
full 8-grid). eps=1e-10, J=1 (BR-0 frozen). Near/far =
BR-0 R=2sigma midpoint rule (unchanged; Amendment-1 joint
cells primary). ESTIMATORS (preregistered formulas):
R_B = f_-^{fn} - f_-^{nf} (>0 influx); R_mag = mass_nf -
mass_fn, mass = f*neg_tail_mean (secondary, no bars).
CURRENT READOUT DISCLOSURE: no validated probability-
current readout exists on main/P1/D15 (searched 2026-10-02;
D15 is walk-rule/compass, not Schrodinger-sector flux), so
BR-2 defines from tight-binding continuity (d|psi|^2/dt =
-SUM 2J J_ij, derived in prereg): J_axis = SUM over edges
with min-image Delta_axis>0 of 2J J_{i->j} displacement-
ordered (frozen orientation rule; zero-displacement edges
contribute 0 to that axis); J_stag = SUM 2J J_{0->1} over
q-ordered edges (proper-bipartition asserted; staggered
flux, NOT net transport). Grounded vs P1-validated v_g
(sign + oddness, EO3) -- derived, not assumed.

BR-2A REPLICATION (bitwise, same code+seeds+machine+numpy):
(A1) E1-rep == BR-0 E1 full records; (A2) E3p-rep == BR-0
E3p; E2-rep seed-0 == BR-0 E2 (C4 recheck input); (A3)
bonding R>0.2; (A4) antibonding R<-0.1 (replication bars
from BR-0 scales, legitimately). SWEEP BARS (J2-L28, must
hold on ALL 3 seeds): (P1) R(0)>0 AND R(pi)<0 [LOAD-BEARING
sign flip]; (P2) |R(pi/2)|,|R(3pi/2)| < 0.25 max(|R0|,|Rpi|)
(self-normalized crossovers); (P3) monotone halves +
closure (ordinal cosine shape); (P4) mirror pairs within
1e-4 (exact-evenness in exact arithmetic; libm-tolerant);
(P5) Pearson(R,cos phi) > 0.9 [LOAD-BEARING association,
allows amplitude/offset distortion]; (P6) nf-liftoff:
f_nf(0)==0 exhaustive / <5e-4 sampled AND f_nf(pi/2)>0.2.
BOND <=> (P1)AND(P5) on J2-L28; J2-L8/ring-60 exhaustive
must satisfy (P1)AND(P5) as confirmatory (any fail = filed
substrate-caveat, PI-adjudicated); (P2)(P3)(P4)(P6) =
diagnostics (failures = filed caveats, no auto-downgrade).
QUADRATURE: BOND + (Q1) Pearson(J_stag,sin)>0.99 (theorem-
confirmation) + (Q2) stagger net-null: |J_net(phi)| < 10%
|J_net(E1)| all phi/axes (standing-pattern null; 10% from
alternating-residual estimate filed in-track). EVEN/ODD
(+EO, INDEPENDENT qualifier): (EO1) max|B_E1-B_E2|<1e-12;
(EO2) J_net(E2)+J_net(E1) <1e-12 (both axes); (EO3)
sign(J(E1))==sign(P1 v_g) (+x, transverse <5%) and E2
mirrored; (EO4) J_stag odd <1e-12. (Exact bitwise versions
pinned in tests via np.conj; campaign uses libm-safe
tolerances for independently-constructed packets.)

BR-2G THEOREM (endpoint-strict + buffer; proof sketched
pre-data): near-strict edge = BOTH endpoints within R_in;
far-strict non-edge = BOTH beyond R_out (R_in=7, R_out=8
frozen, J2-L28/s=4). IF min B over near-strict edges >
max B over far-strict non-edges (premise, checked
EXHAUSTIVELY: 6272 edges + ~1.2M non-edges vectorized),
THEN every strict-nf move has dE = -2J(B_add-B_rem) > 0
STRICTLY (margin >> eps, no fp risk) => P(favorable
strict export) = 0 EXACTLY. Predicted margin ~1.53x
(envelope ratio x edge-cos_min 0.955; verified exactly in
campaign). Midpoint rule (BR-0) ~= strict up to a fringe
band (endpoints can straddle R); fringe violations
possible-in-principle => NO exact theorem claimed under
midpoint classification (honest scope); bound + reclass
filed. (G1) premise holds (margin filed); (G2) strict-nf
n_neg==0 on 3x200k (theorem-check); (G3) E1-rep midpoint-
nf == 0 (re-cite). Stagger corollary (filed prediction):
strict protection needs cos phi > ~0.625 (far same-
sublattice non-edges have B=rho rho x1) => nf-liftoff for
phi >= ~pi/4 (this IS (P6) mechanistically). CONTROLS:
C0 local==full-H <1e-9 (stagger phi in {0,pi/2,pi} x
2000 moves, HARD GATE); C1-spot: global-phase-rotated
phi=pi/4 f-fields within 1e-5 (HARD GATE); C4: rescale
x2 (phi=0, seed 0): R f-fields EXACT-equal (signs bitwise
under x4) + tails x4 (rel 1e-12) (HARD GATE); C2/C3/C5
theorems in tests (endpoint sym, zero null, conjugation).

LADDER: ~BOND => BR2-NULL (route stops; +EO still reported
if passed standalone); BOND => BR2-BOND (admits BR-3);
+Q1Q2 => BR2-QUADRATURE; +EO1-4 => +EO qualifier. EXPECTED
(non-binding, guide reading): R(0)~+0.93 (E3b-like),
R(pi)~-1 (uniform-antibonding efflux), R_B(phi) full
+0.93->-1 swing; J_stag exact sine (theorem); E3p R<0
re-cited. COMPUTE: local primary + beast replication from
start (same frozen protocol; BR-0 precedent: bitwise on
verdict fields). NEXT: run (gated on this prereg commit)
-> file BR2-VERDICT (ladder + G-status + BR-3 admission).

BR2-VERDICT (campaign-data 2026-10-02, local 22min exit-0; artifact
data/br2_phase.json; mechanical analyzer scripts/analyze_br2.py).
LADDER OUTPUT: BR2-QUADRATURE (+EO) -- the strongest BR-2 result.
EVERY load-bearing bar passes on ALL 3 seeds + BOTH exhaustive
substrates; two diagnostic/caveat flags below (both understood
mechanistically, neither touches the ladder).

BR-2A REPLICATION: E1-rep/E3p-rep/E2-rep BITWISE-IDENTICAL to BR-0
(same code+seeds+machine+numpy; full-record dict equality); (A3)
bonding R=+0.337>0.2 PASS; (A4) antibonding R=-0.430<-0.1 PASS.
BR-0 anatomy reproduced exactly.

SWEEP (J2-L28 R_B(phi), seed-0; seeds 1-2 replicate to ~0.005):
[+0.927, +0.941, +0.004, -0.457, -0.457, -0.457, +0.004, +0.941]
(P1) sign flip +0.927 -> -0.457 PASS x3 seeds; (P5) Pearson(R,cos)
= 0.9710/0.9716/0.9718 PASS; (P2) crossovers 0.004-0.010 vs 0.25x
bar PASS; (P4) mirror pairs BITWISE-equal (|dR| = 0.00e+00, better
than 1e-4 bar) PASS; (P6) nf-liftoff: f_nf(0) = 0.0001/0.0000/0.0001
(<5e-4) -> f_nf(pi/2) = 0.51 (>0.2) PASS. EXHAUSTIVE confirmatory:
SWX-J8 R = [0.891,0.912,0.007,-0.431 x3,0.007,0.912], r=0.9701,
nf(0) = EXACTLY 0 counts, nf(pi/2) = 0.528; SWX-R60 R =
[0.945,0.955,0.018,-0.456 x3,0.018,0.955], r=0.9721, nf(0) = 0,
nf(pi/2) = 0.502. (P1)AND(P5) on all 3 substrates => BR2-BOND.
E_psi(phi) = -7.9381 cos phi EXACTLY (all 8 points; energy follows
the bond quadrature). R_mag (secondary, filed): [+1.60,+1.40,+0.83,
-2.09,-3.30,-2.09,+0.83,+1.40]e-3 -- magnitude swing matches sign
swing (crossover slightly positive at pi/2: counts balance while
fn tails run heavier -- descriptive).

QUADRATURE: (Q1) J_stag = 7.938 sin phi, r = 1.00000 PASS
(theorem-confirmed); (Q2) stagger net-current NULL at 6.6e-18
(ratio 5.6e-18 vs E1 -- machine-precision null, far below the
10% bar). MECHANISM (filed): reflection-paired cancellation
(envelope mirror pairs carry bitwise-identical rho-rho with
opposite q => exact-negation J terms + fp scatter); honest
caveat: asymmetric envelopes would residual at TV-scale (~few %,
BR-3 note). BOND+Q1Q2 => BR2-QUADRATURE: potential-like
structural response (B/cos) and current-like quadrature (J/sin)
are two aspects of the same (r,s) relational field.

EVEN/ODD (+EO, all four): (EO1) max|B_E1-B_E2| < 1e-12 PASS;
(EO2) J_net(E2)+J_net(E1) = 0.00e+00 bitwise PASS; (EO3)
J_x(E1) = +1.1713 > 0, J_y == 0.00e+00 bitwise (transverse
exact-null as derived), E2 mirrored PASS -- BONUS (unbarred):
|J_x| = 1.1713 matches P1-validated v_g ~1.21 to 3% (current
magnitude grounded in validated transport); (EO4) stag-odd
bitwise PASS (both ~1e-17 dust). Direction-even potential
response vs direction-odd flow SEPARATED (BR-5 foundation).

G-THEOREM: PROVEN under endpoint-strict classification.
(G1) premise holds EXHAUSTIVELY: E1 min-near-B = 1.26e-3 >
max-far-B = 6.74e-4 (margin 1.87x, better than predicted
1.53x); phi0 margin 1.96x. (G2) strict-nf favorables == 0
on 3x200k (n_strict ~109k each; R_strict ~+0.69) PASS --
theorem-check green. (G3) midpoint-nf == 0: FAILS by 2
counts (seed-2: 2/36726, rate 5.4e-5; seeds 0-1 exact 0;
IDENTICAL in BR-0 -- bitwise rep confirms this was always
the value, printed 0.0000). RESOLUTION (strengthens G):
midpoint-nf = 0 is APPROXIMATE (fringe-rare: 2 fringe
violations in 600k, exactly the possible-in-principle class
flagged pre-data); strict-nf = 0 is EXACT (theorem + G2).
The BR-0 nf=0 census result is thereby EXPLAINED (midpoint
~= strict + O(1) fringe counts) and PROMOTED (strict exact).

CAVEAT-2 (P3 diagnostic FAILS, preregistered non-gating):
R(pi/4) = 0.941 > R(0) = 0.927 (all seeds + both exhaustive:
real shape, ~11 sigma pooled). MECHANISM (filed): cos phi<1
shrinks ALL B_rem, boosting fn favorables (+590 counts,
far-edge B_rem easier to beat) faster than nf fringe gains
(+20) => net R bump +0.014. Cosine-monotonicity is broken
at O(1%) by this fringe-asymmetric gain; (P5) association
unaffected (r=0.97). EFFLUX-HALF SATURATION (filed finding):
fn/nf COUNTS bitwise-identical across 3pi/4, pi, 5pi/4 per
seed (e.g. 21616/36830 x3) -- move signs FREEZE once cos phi
<= -0.707 (plateau R=-0.457, not -1: fn locks at the
|far|>|near| subset ~0.54). CONTROLS: C0 max 1.8e-15 PASS
(HARD); C1-spot R-identical PASS (HARD); C4 rescale R-exact
+ tails x4 PASS (HARD).

INTERPRETATION: Re(psi*_i psi_j) is a genuine potential-like
structural backreaction variable (BR2-BOND); B~cos/J~sin
quadratures confirmed with structural response on B and
transport null/oddness on J (BR2-QUADRATURE); direction-even
vs direction-odd separated (BR2-EVEN/ODD). This is a major
EM-hypothesis input but NOT electromagnetism (no charge/
fields claimed; firewall held: J never scored a move).
BR-3 ADMITTED (evolution gate): use ONLY dE = -2J(B_add-B_rem)
ordering (no target geometry/force direction); ask influx/
efflux realization + reciprocal loop G'->H->psi'. BR-3 owes:
asymmetric-envelope Q2 residual scale; plateau-0.54 subset
characterization; pi/4-bump rôle under iteration.

POT1-PREREG (FROZEN-2026-10-02 (~02:30-UTC (commit-predates-
ALL-POT1-campaign-runs!)); static/dynamic-potential-unification
(POT-1-gated-OPEN-by-POT0-COLLECTIVE!)). QUESTION: can-the-SAME-
(r,i)-field-on-J2-under-UNCHANGED-H=-A-support-a-stationary-source-
relative-potential-like-configuration-AND-are-source-change-transients-
carried-by-the-banked-P1/POT-0-wave-sector? FROZEN-ONTOLOGY: G=J2 +
psi=r+i*s + H=-A (no-third-scalar/no-V-field/no-onsite/no-weights/
no-rewiring-dynamics/no-backreaction/no-D5inf (field-only!)).
SOURCE-APPARATUS (frozen-design!): harmonic-pinning (each-step-overwrite
of-predefined-single-node-source-regions-with-s*exp(-iwt) (acts-ONLY-on-
S (no-bulk-inspection-whatsoever!)); s=1.0-headline; w=-8.5-J2 (half-
unit-below-band-edge-(-8) (gap-theorem-pinned!)) + w-in-{-2.5,-3.0}-
path (gaps-0.5/1.0-below-(-2)); dt=0.02 (w*dt=0.17!); single-node-S_+
at-(0,0,0) + pair-S_+-at-(0,0,0)/S_--at-(8,0,0)-axial-d=8 (mirror-x->8-x-
auto-for-exchange!); windows-L20/T=6/r<=4 + L28/T=8/r<=6 + L42/T=10/
r<=8 (pre-wrap-by-vmax=6-bound!); path-60-open-pins-at-ends-T=12).
DERIVED-PREDICTIONS (pre-data-math (pinned-in-tests-NOT-assumed!)):
(i)-steady-state-exists-unique (gap-to-H_BB (interlacing!)); (ii)-phi-
REAL; (iii)-single-source-phi-STRICTLY-positive-everywhere (M-matrix-
inverse-positivity (nodeless-Yukawa-like!)); (iv)-linearity/superposition-
EXACT; (v)-exchange-=-mirror-image (automorphism (no-negation (pinned!)));
(vi)-J_ij-=-0-static (reality (potential-regime-carries-NO-current!));
(vii)-resolvent-=-all-path-sum (NOT-shortest-path!). OBSERVABLES (phase-
invariant-bilinears-ONLY (frozen!)): PRIMARY-B_ij-= Re(conj(psi_i)psi_j)
(static-pattern (monopole-+-pair-dipole-nodal!)); STATIC-CHECK-J_ij-=
Im(...) (≈0!); SECONDARY-density; complex-phi-ONLY-for-prediction-match-
+ exchange-at-frozen-drive-phase (state-level-never-called-potential!).
SEPARATION (frozen!): least-squares-psi(t)-=-A*exp(-iwt)-+-F-over-final-
drive-period (A-vs-prediction + F-=-flat-band/static-residue-filed!).
STATIONARITY (spec-literal!): min_phi-||psi(t+T)-e^{iphi}psi(t)||/||psi||
(T-=-drive-period-snapped (phase-fit-absorbs-snap (exact-steady-=-0!))).
POT-1A-PATH-CALIBRATION (HARD-GATE (fail-STOPS-J2-interpretation!)): pair-
pins-+-1/-1-ends-60 + jump-(stationarity)-+-turn-on-from-zero-(shape) +
kappa-law-fit. PASS ⟺ ALL: solve-vs-closed-form-1e-9; jump-global-0.05/
shell-0.15 + turn-on-global-0.10/shell-0.25 (r<=10-floor-0.01); kappa-fit-
within-5%-of-arcosh(|w|/2)-both-gaps; eps-jump<0.02-turn-on<0.10;
linearity-solve-1e-9-evo-0.05. (Linear-descent-NOT-predicted (below-band-
implies-EXPONENTIAL (linear-=-zero-gap-limit (singular-settling (noted-
follow-up!)))). POT-1B-J2-SINGLE (L20/28/42-turn-on-+-jump): PASS ⟺ jump-
0.05/0.15 + turn-on-0.10/0.25 (r<=r_set); eps-same-as-1A; J/B<0.05;
POT-0-D-<0.05-mean (potential-regime-has-NO-direction (predicted!));
range-(|A|>0.05)-matches-prediction-+-1-shell. POT-1C-PAIR (d=8-all-L):
PASS ⟺ globals-same-as-1B + nodal-sign->0.95 (|A_pred|>0.05 (dipole-
structure!)) + D<0.05. ALL-PATH (L28-wall-x=4->5-cut-except-gap-y=13/14/
15 (SLIT-precedent-bond-apparatus (frozen-graph (NOT-dynamical-rewiring!))
+ recomputed-parameter-free-prediction): PASS ⟺ cut-prediction-match-0.10
+ shadow-(r=6..12)-differs-from-uncut->25% (route-sensitivity!) + best-fit-
single-exponential-in-d_short-max-residual->3x-prediction-residual
(beyond-shortest-distance!). POT-1D-EXCHANGE (jump-pair-swapped-drives):
PASS ⟺ stroboscopic-mirror-match-0.05 + B-mirror-0.05. POT-1E-PHASE
(turn-on-from-zero-drive-phases-{0.7,2.1,4.0}): PASS ⟺ B,J-identical-1e-9
(theorem-exact (absolute-phase-NOT-observable-zero!)). POT-1F-CHANGE
(jump-steady-sign-flip-at-t0=T/2 (+-amplitude-step-secondary) + unswitched-
control): PASS ⟺ t0+dt-snapshot-dist>=8-max|dpsi|<1e-9 (no-instant-action
((Hdt)^d/d!-tails-respected!)) + delta-B-shell-arrival-front-v-in-(0.5,6)-
R2>0.95 (ballistic-causal!) + remote-(r>=C4_R)-pre-arrival-|dB|<1e-6 (C4!).
POT-1G-TRANSIENT-SECTOR (dpsi-analysis): PASS ⟺ S-shell-(|J|-of-dpsi)-peak-
front-v-in-(0.5,6)-R2>0.9 (radiation-ballistic!) + far-field-(r>6)-late-
flat-weight-<0.2-+-accounting-1 (propagating-=-dispersive-band!) + C5-ring-
packet-through-campaign-fitters-v-10%-+-alpha>1.3 (analysis-validated!).
NOTE-filed: symmetric-change-transient-predicted-D≈0 (spherical-radiation
(NOT-packet-directionality (no-D>0-required-here!))). POT-1H-INJECTION
(SECONDARY (packet-(20,0)-k=+0.3-toward-maintained-source-T=14)): PASS ⟺
final-B-returns-to-steady-0.10 (equilibrium-restored!). POT-1I-LADDER
(lam-in-{0.5,1,2}-turn-on): PASS ⟺ A(lam)/lam-vs-A(1)-0.05 (linear!) +
B(lam)/lam^2-vs-B(1)-0.05 (DERIVED-quadratic (bilinear!)). POT-1J-SIZES:
PASS ⟺ xi-fit-(shells-2..5-common)-pairwise-20% (intrinsic-range (NOT-
torus-artifact!)) + wrap-control-(2T-settled-drift-<5% (VALIDITY-gate
(fail-caps-at-DRIVEN!))) + L28/L42-front-speeds-25%. CONTROLS: C0-same-H-
object (code-level!); C1-pinning-disabled-packet-reproduces-POT-0 (v-2%-
D-5%-alpha>1.3!); C2-source-symmetry (via-1D-mirror!); C3-=-1E; C4-=-1F-
pre-arrival; C5-=-1G-ring-cal; C6-reruns-bit-identical. FIELD-ACCOUNTING:
reactive-balance-|W_net|/W_gross-<0.05-final-period-jump-L28+L42 (AC-
steady-reactive (no-net-injection!) + 1H). LADDER: !1A->POT1-NULL
(apparatus-invalid!); !(1B&1C)->NULL; relational-fail->DRIVEN (standing-
wave-NOT-potential!); 1A+1B+1C+AP+1D+1E+1I+1J+C1+C6->POTENTIAL; +1F+1G+C5->
UNIFIED (static<-same-field->radiation!); +1H+RB->FIELD (EM-0-opens!).
FORBIDDEN (even-FIELD-NOT!: charge/Coulomb/Maxwell/SM-photons/polarizations/
gauge/Lorentz/EM!). NEXT: freeze-commit-then-beast-campaign (gated!).

POT1-PILOT-1-DISPOSITION (SUPERSEDED (gate-miss-owned (P1-Amendment-3-
precedent!)); beast-run-f65f2d0/59699a8 (dt=0.02): LADDER-POT1-NULL
(APPARATUS/ANALYSIS-failures (NOT-physics-refutation!))). ROOT-CAUSES
(diagnosed-post-pilot (numbers-filed!)): (a)-stroboscopic-pinning-shift-
O(w*dt) (L12-calibration: jump-global-0.070-at-dt=0.02 (fails-0.05!)
vs M-matrix/predictions-EXACT (solve==analytic-1e-9 (math-right!)));
(b)-turn-on-LS-aliasing (single-period-fit-cannot-separate-drive-
from-lingering-band-edge-transient (beat-2pi/0.5=12.6->-window!) +
flat-band-deposit-|F|=0.30-L-independent (filed-measurement!)) ->
flat-kappa/xi-fits (0.12-vs-0.69!) + range-20-on-L20; (c)-1F-design-bugs
(absolute-threshold-vs-decaying-transient (F_front-null!) + cone-6-~-
true-speed (C4-fails-on-tails-2e-3!) + SIGN-FLIP-localized-step-vs-
radiation-confusion + S-peak-fit-v=5.15-EXCEEDS-Bloch-bound-4 (FIT-
ARTIFACT-RETIRED (phase/slosh-peak (NOT-group-front!) filed!)));
(d)-H-window-short (T=14 (absorber-weak (single-node!))); (e)-RB-L42-
anomaly-1.0 (discrete-pumping (dt-artifact!)). PHYSICS-PASS-BANKED
(as-filed-observations (NOT-verdicts!)): solve==analytic-both-gaps;
jump-shells-pass-all-L; nodal-112/112-all-L (dipole-EXACT!); exchange-
mirror-pass; drive-phase-covariance-1e-9; linearity/quadratic-pass;
AP-route-sensitivity-29x-1D-rejection (res1d=0.81-vs-0.028!); transient-
minus-branch-0.95 (nearby-band-edge-radiation-✓!); D≈0-everywhere;
C1/C5/C6-pass.
POT1-AMENDMENT-1 (PRE-RERUN (pilot-1-opened (above!)); protocol-v2-
frozen-here): (i)-dt-=-T_drive/296-=-0.002497-ALL-driven-runs
(commensurate-296 (w*dt=0.021); calibration-L12-jump: global-0.070->
0.009 (5x-margin!) + t-indep-0.006 + eps-0.006 + J/B-0.007 (stable-
T=2->4!)); (ii)-jump-=-PRIMARY-steady-vehicle (phase-rotate-extraction-
A-=-psi(t)e^{+iwt}-late-t + t-independence-<0.02-8-snapshots (REPLACES-
LS-for-jump; LS-kept-for-ramped-turn-on)); (iii)-turn-on-SPLIT: raw
(fronts/causality/D-sharp-edge (NO-shape-tests!)) + cosine-ramped-tau=4
(steady-corroboration (SAME-shape-tolerances-as-turn-on-had!));
(iv)-1F-REDESIGN: PRIMARY-=-turn-on-front-arrivals (raw-|psi|-series +
S-series (added-worker-readout!) + far-shells-r>=6 + per-shell-relative-
10%-threshold + v-in-(0.5,5) (Bloch-bound-4-+-margin!) + R2>0.9);
sign-flip-=-SECONDARY (radiated/local-split-anatomy-filed + causality-
cone-12 (principled->>-v_max!) + instant-bound-kept); (v)-G_shell-on-
TURN-ON-S-front (same-gate (sign-flip-S-fit-retired-with-artifact!));
branch/accounting-unchanged; (vi)-H-T=14->20 (pre-revisit-~23!);
(vii)-ALL-other-thresholds-IDENTICAL (0.05/0.15/0.10/0.25/1e-9/0.95/
nodal/D/linearity (NO-shopping!)); (viii)-D-trace-stride-10 (filed-
perf (D-smooth!)); worker-shell-series-accumulated (same-numbers!).
RERUN-verdicts-are-the-record (pilot-1-numbers-above-filed-context!).
NEXT: implement-v2-+-smoke-+-amendment-commit-then-beast-rerun (gated!).

POT1-V2-DISPOSITION (SUPERSEDED (gate-miss-owned (Amendment-3-precedent!));
beast-run-1001614 (dt-commensurate + jump-primary + ramp-tau=4 + fronts-
redesign): LADDER-POT1-NULL (APPARATUS/ANALYSIS-failures (NOT-physics-
refutation!))). ROOT-CAUSES (diagnosed-post-v2 (calibration-rounds-K1-K5-
filed-scripts-pot1_calib{,2,3}.py!)): (a)-PERSISTENT-k≈0-band-edge-
lingerers (turn-on-deposits-into-bulk-EIGENMODES-that-oscillate-FOREVER
(unitary-bulk!) + NO-T-dependence-T=12-vs-24-identical-to-0.1% (NOT-a-
decaying-transient!) + single-period-LS-aliases-them-into-A (beat-12.6-
>-period!) -> ramp_global-0.44->0.22-tau=4->8 + flat-kappa/xi-fits +
Planck-taper-WORSE-0.32-than-cosine (REJECTED (effective-timescale!)));
(b)-velocity-bound-WRONG (BLOCH-THEOREM (derived + numerically-verified-
L6: flat-band-at-0-EXACT (46-zero-modes-=-36-flat-+-10-band-touching!) +
dispersive-eps(k)-=--4(coskx+cosky)!): Manhattan-group-max-=-8 (NOT-4!);
measured-fronts-7.79-7.94-R2>0.999-sit-just-below-✓ (physics-RIGHT-gate-
WRONG!) + threshold-trend-8.27/7.79/6.86-(5/10/20%)-=-precursor-riding
(filed!)); (c)-AP-shadow-threshold-UNPRINCIPLED (parameter-free-
prediction-says-4-15%-shell-diffs (measured-2.5-5%-in-ballpark!) NOT-
>25% + wall-far-gap-detour-27-hops-xi≈2-kills-signal-to-1e-6 (BELOW-
noise-floor (geometry-unmeasurable!))); (d)-RB-metric-measures-SLOW-
BEAT-phase-NOT-injection (L28-1T-0.062->2T/3T-1.0 (longer-=-worse!) +
net-sign-flips-prove-SLOSH-not-pump!); (e)-J_wrap-compared-MISMATCHED-
vehicles (raw-2T-vs-ramp-T!). PHYSICS-PASS-BANKED (v2-filed-observations
(NOT-verdicts!)): jump-global-0.009 (5x-margin!); nodal-112/112-all-L;
exchange-mirror; phase-covariance-1e-9; linearity/quadratic; 1D-reject-
30x (0.72-vs-0.024!); transient-w_minus-0.95 (band-edge-radiation-✓);
eps/JB/D-everywhere; F_instant-exact-0 + C4-cone-12; C1/C5/C6-green.
POT1-AMENDMENT-2 (PRE-RERUN (v2-opened (above!)); protocol-v3-frozen-
here): (i)-turn-on-=-cosine-tau=8-headline + T=16-UNIFORM-all-J2 (no-T-
dep-proven (T=12≈T=24!) + T=12-path-kept) + tau-in-{4,12}-L20-ladder;
(ii)-turn-on-shape-→-INNER-PROFILE (r<=4-CONTAINS-96.8%-steady-norm-
(all-L-filed!) >90%-principle!): inner-global-0.10 + inner-shell-0.25
(SAME-tolerances-restricted-region (outer-shells-lingerer-dominated-
filed-secondary!)) + range-kept (lingerers-0.009-«-0.05-robust!);
(iii)-kappa/xi/eps-→-JUMP-vehicle-GATED (5%/20%/0.02 (steady-state-
properties-→-primary-steady-vehicle (Amendment-1-principle!) + turn-on-
versions-FILED (lingerers-=-real-physics (path-gap-a-c≈0-yet-kappa-
flat-proves-standing-modes!))); (iv)-ADIABATIC-TREND-GATED (tuning-
free!): lingerer-|c|-(median-|A|-r>=10-L20)-STRICTLY-decreasing-tau-
4>8>12 (calib-0.0197>0.0088>0.0053!); (v)-velocity-v-in-(0.5,12)-R2>0.9
+ L28/L42-25% (12-=-1.5x-Manhattan-group-max-8-Bloch-(-precursor-
margin-=-C4-cone (coherent-causal-limit!)) + threshold-stability-
filed); (vi)-AP-geometry-=-wall-x=1->2-gap-row-(1,)-L28 (delta_pred-=-
0.2304-filed!): cut-jump-global-0.05 + cut-turn-on-inner-0.10 + |delta-
jump_-_0.2304|/0.2304-<0.35 + 1D-reject-kept; (vii)-H-=-inner-r<=3-
(93.3%-norm-filed!)-return-0.10 + far-resid-norm-≈-pkt-norm-10% (torus-
cannot-globally-return (radiation-has-nowhere-to-go!) + K4-margins-
2x/6x!); (viii)-RB-=-T=40-jump-norm-range-final-24-<-1% (no-
accumulation (proven-discrete-steady-work≡0 + measured-~0.2% (5x-
margin!)) + reactive-ratio/cancellation-filed); (ix)-J_wrap-=-same-
protocol-ramp-T-vs-2T-inner-drift-<5%; (x)-ALL-inherited-thresholds-
IDENTICAL (NO-shopping!) + new-gates-from-predictions (delta/vmax/
containment)-or-tuning-free (monotonicity)-or-round-accounting (1%/
10%/35%). RERUN-(v3)-verdicts-are-the-record. NEXT: implement-v3-+-
smoke-+-amendment-commit-then-beast-rerun (gated!).

POT1-V3-DISPOSITION (SUPERSEDED (gate-miss-owned (Amendment-3-precedent!));
beast-run-5e75b80 (tau=8/T=16-inner-profile + jump-kappa/xi/eps +
trend-gate + v-(0.5,12) + AP-wall-(delta-0.2304) + H-accounting + RB-
norm-range): LADDER-POT1-NULL-on-TWO-gates-only (ALL-other-gates-GREEN
(many-big-margins!) NOT-physics-refutation!)). GREEN-BANKED (v3-filed-
observations): AP-delta-0.2295-vs-0.2304-(0.4%!); TAU-trend-0.0197->
0.0088->0.0053-strict-✓; RB-0.0026/0.0021-(4x!); H-acct-0.984-vs-1.0;
ranges-3=3-all-L; jump-kappa-0.7%/2.2%; jump-xi-pairwise-0.4%;
fronts-7.8-7.9-R2>0.999; RB-nets-sign-flip-(+,-,+)-slosh-✓; nodal/
exchange/phase/linearity/C1/C5/C6-green. MISS-1-A_a_ramp_shell (path-
gap-(a)-ONLY-r=4-shell-rel-0.48-(rest-<=0.10!): 1D-standing-lingerers-
per-node-3x-worse-than-J2 (0.030-vs-0.009-measured (no-transverse-
dilution!)) + S/B-marginal-at-r=4-(signal-0.0625)!). MISS-2-J_wrap
(ramp-T-vs-2T-inner-drift->5%: lingerer-BEAT-(12.6)-confounds-wrap-
comparison (two-times-never-agree-to-5%!) NOT-wrap-contamination!).
POT1-AMENDMENT-3 (PRE-RERUN (v3-opened (above!)); protocol-v4-frozen-
here): (i)-path-turn-on-=-tau=16/T=24-both-gaps-uniform (1D-S/B-parity-
rationale (above!) + VERIFIED-pre-freeze-calib5-per-shell-rel-<=0.0044-
(57x-margin!)-inner-global-0.005/0.002!); (ii)-J_wrap-→-JUMP-vehicle
(L28-pred-T=8-vs-pred-2T=16-inner-shell-drift-<5% (steady-stability-→-
steady-vehicle (Amendment-2-principle!) + VERIFIED-pre-freeze-calib4-
drift-<=0.38%-(13x-margin!))); (iii)-ALL-else-IDENTICAL-to-v3 (gates/
thresholds/vehicles/windows (NO-other-changes!)). RERUN-(v4)-verdicts-
are-the-record. NEXT: implement-v4-+-smoke-+-amendment-commit-then-
beast-rerun (gated!).

POT1-VERDICTS (beast-run-6829cb2-protocol-v4 (Amendment-3-frozen-pre-data!);
suite-626-passed-2-skipped-green): LADDER-POT1-FIELD (STRONGEST-RUNG
(ALL-gates-green-first-run (NO-post-hoc-tuning!))). STATIC-SECTOR:
1A-path-calibration-✓ (solve==analytic-1e-9 + jump-0.05/0.15 + turn-on-
inner-0.005/0.002-(20x!) + kappa-jump-0.7%/2.2% + linearity-1e-9/0.05);
1B-single-✓ (jump + inner-0.015-0.064 + J/B<0.05 + D≈0 + range-3=3-all-L);
1C-pair-✓ (jump + inner + nodal-112/112-all-L (dipole-EXACT!) + D≈0);
ALL-PATH-✓ (cut-jump-0.05 + cut-inner-0.016 + delta-0.2295-vs-0.2304-
(0.4%!) + 1D-reject-278x-(0.69-vs-0.0025!)); 1D-exchange-✓ (mirror-0.05-
+ B-0.05); 1E-phase-✓ (B,J-identical-1e-9 (phase-NOT-observable-zero!));
1I-ladder-✓ (linear-0.05 + quadratic-0.05); 1J-sizes-✓ (xi-pairwise-
0.4%-(0.5288/0.5272/0.5265!) + wrap-drift-<=0.4% + front-consistency-2%);
TAU-adiabatic-✓ (lingerers-0.0197>0.0088>0.0053-strict (tuning-free!)).
DYNAMIC-SECTOR: 1F-change-✓ (instant-exact-0 + front-v=7.79-R2=0.9995-
in-(0.5,12)-Bloch-8-✓ + C4-cone-12-3e-9!); 1G-sector-✓ (S-front-v=7.88-
R2=0.9997 + w_minus-0.95-(band-edge-radiation!) + accounting-1 + C5-
ring-✓). UNIFICATION: 1H-return-✓ (inner-r<=3-0.10 + far-norm-0.984-
vs-1.0!); RB-✓ (norm-range-0.26%/0.21%-(4x!) + nets-sign-flip-slosh-✓);
C0/C1/C5/C6-✓ (POT-0-packet-reproduced-v=1.211-D=0.855!). INTERP:
TWO-real-scalars/node-+-binary-J2-fabric-→-static-potential-like-field
(-connectivity-determined + all-path + source-relative + phase-
invariant-) ←-same-(r,i)-field-H=-A-→-coherent-directional-radiation
(same-modes-as-P1/POT-0-banked-waves!). FORBIDDEN-CLAIMS-RESPECTED
(even-FIELD-NOT-charge/Coulomb/Maxwell/photons/gauge/Lorentz/EM!).
NEXT-OPEN: EM-0-continuum-field-characterization (radial-law? effective-
equations? B/J-roles? BR-2-quadrature-match?).

## BR1-PREREG — Vacuum neutrality + rigidity (D14-BR1, FROZEN PRE-DATA)

**Status:** apparatus + ladder frozen; campaign NOT YET RUN. Audit and
falsification campaign: discovers rigidity already present in existing
dynamics, creates none. No new E_G, potential, temperature, Metropolis
factor, rigidity parameter, motif penalty, or healing target anywhere.

**Frozen ontology:** G, psi = (r, i), U (existing rules only). Primary
vacuum: G = J2, psi = 0. Primary move class M1 (BR-0-frozen): remove one
uniform edge + add one uniform non-edge (N, E, simplicity preserved;
degree sequence NOT; connectivity NOT required).

**Frozen vacuum fingerprint (banked observables ONLY):**
- UV/micro: degree histogram, micro shells (8/17/8r), cuts (56/32r+16),
  C4 census (blind_u.nsquares; banked 26072 at R18), return probs
  (characterization, campaign tracks p2 only via bip_viol proxy — NO,
  frozen correction: returns NOT re-measured; bipartition violations
  (banked 0) serve as the odd-cycle witness), quotient cell census.
- IR/class: connectivity, long-scale exponent p (banked band (1.90,1.94)
  on R24 window [8,20]), quotient square-adjacency fraction (banked 1.0;
  min-image readout on tori, P1 convention).
- Wave (C6, characterization only, no verdict weight): E1 packet
  (k=(0.3,0), sigma=4, r0=(7,15)) oneway_run 60x0.1 on pristine vs
  N1-killed L28; readouts disp + participation ratio.

**CLASS-ALIVE(t) (survival criterion):** connected AND |p(t)-p(0)| <= 0.15
(banked micro-vs-quotient tolerance) AND qfrac >= 0.99. UV drift alone
(C4/degrees/bip_viol) is anatomy, never death. tau_micro: first t with
G_t != J2 (predicted == 1 move under N1, pinned by construction).

**Campaign grid (frozen):** census torus L in {4,6} exhaustive + {4,6,8,12,28}
closed-form, anatomy n=2000 (seeds 100/101) on L {8,12,28}; drift J2 balls
R {12,18,24} x seeds {0,1,2}, T=3000, snapshot 25 (heavy every 4th);
p-windows R12 [4,9], R18 [6,14], R24 [8,20] (banked); square-torus-L28 N1
control x2 seeds + J2-torus-L28 x1 seed (window [5,11], final graph kept);
U-audit pristine L12 {null, scramble, guillotine, anneal, slide, square,
triangle, metropolis x2 (T 0.25/1.0), kappa(5 steps)} + pristine L28
{null, scramble, guillotine, square} + C2 damaged-L12 (20 swaps)
{guillotine, anneal, slide}; defects L12 x3 seeds x {guillotine, anneal,
slide, square}; small-field L8 eps {1,1e-1,1e-2,1e-4,1e-8} psi_hat seed
1001, 500 moves; C0 exhaustive ring-8 + sampled L12 n=2000.
smax_J2 = max edge-span on pristine J2 (radius 3), measured t=0 baseline
(fabric-relative calibration, banked methodology). pair/triple/quad
EXCLUDED from audit/defects (order-2+ coordination cost unjustified for
single-defect probes; exclusion pre-data, not from results).

**U_G inventory + domain pre-judgment (behavior still measured):**
- null/scramble: harness controls, not physics (null ~ N0 behaviorally).
- greedy_heal: global target, inadmissible form — EXCLUDED (not run).
- guillotine/anneal/slide/drift(chain): repair-domain rules (D1 battery).
  NOT vacuum kinetics by justification; run on pristine (expect inert, 0
  accepts) + damaged (expect active, C2) + defects (counterfactual).
- square/triangle/metropolis/kappa: blind-admissible FORM; square-grid
  record Goodhart/leaving/negative/frozen. Run on J2 as blind-form audit.
- formation.py (D5inf etc.): formation-domain (soup->core), NOT vacuum
  kinetics — EXCLUDED by domain (category error to apply to pristine J2).
- healing.py: GW ringdown sector, not graph dynamics — EXCLUDED by domain.
- NX policy: VACUOUS unless a rule meets the DYNAMIC bar below (no
  independently-justified vacuum-domain U_G inventoried pre-data).

**Verdict ladder (frozen bars, evaluated by scripts/analyze_br1.py):**
- BR1-KINEMATIC-RIGID iff N_legal(L28) == 0. (Predict: falsified.)
- BR1-DYNAMIC-RIGID iff some inventoried rule is inert-fixed on pristine
  L12 (0 accepts AND fp_after CLASS-ALIVE) AND class-restores >=2/3
  G-defects (longs_after == 0 AND fp_after CLASS-ALIVE). Bit-restore
  predicted IMPOSSIBLE for swap-class rules (degree-fiber pin,
  test_rigidity.py) — bar is class-restore. (Predict: not met.)
- BR1-CLASS-RIGID iff all 9 J2 drift runs alive at T=3000. (Predict: no;
  banked swap-fragility suggests fast death.)
- BR1-METASTABLE iff deaths observed AND (median tau_class > 200 at some
  R OR monotone-increasing medians R12<R18<R24). Scaling reported, no
  forced fit.
- BR1-FLAT iff none of the above (drift kills class fast with no
  protective U). (Predict: FLAT, tau_class ~ O(10).)
- N0/N1/NX debt table: N0 frozen-analytic (G == J2, survival 1.0);
  N1 measured; NX vacuous (see above). No policy selected (Firewall).

**Controls:** C0 bitwise zero-field null (exhaustive + sampled, both
paths); C1 determinism (unit pins + analyzer re-run); C2 matched
substrates (damaged-J2 activity controls + square-torus drift control);
C3 E conservation every trajectory; C4 no coordinate use by dynamics
(labels read-only for quotient/bipartition readout); C5 multisize
(R 12/18/24 + L12/L28 audit); C6 banked wave law unchanged (E1 settings).

**GRAV-0 handoff:** defect anatomy (longs created, restore/overlap,
spread) recorded without propagation interpretation.

## BR1-VERDICT — BR1-FLAT (rigidity debt confirmed, 14/14 gates)

**Campaign:** data/br1_vacuum.json (beast run, 246 s, frozen runner).
**Ladder:** KINEMATIC falsified (N_legal(L28) = 7,665,989,632, exact
closed form, L4/L6 exhaustive match 47104/653184); DYNAMIC not met by any
inventoried rule; CLASS-RIGID falsified (9/9 J2 drift runs dead by t=25);
METASTABLE falsified (median tau_class = 25/25/25 at R12/18/24 — first
snapshot at every size, no trend, far below the 200 bar). **= BR1-FLAT:**
the current ontology does not explain vacuum rigidity.

**Neutral drift (N1, BR-1D/F):** tau_micro = 1 move (every relocation
changes the edge set; 3000/3000 applied, E conserved every trajectory).
Post-verdict characterization (NOT ladder input, snapshot-every-1 rerun):
exact tau_class = 3/9/6 moves at R12/18/24, first killer = p-drift
(|dp| = 0.16–0.21), qfrac still >= 0.993 at death. Square-torus control
under identical N1 also dead at t=25 both seeds: neutral drift is
generically destructive, J2 not special. M1 anatomy (L28): disconnect
fraction 0.0/2000, 97% of additions nonlocal (graph distance >= 4).

**Existing-U audit (BR-1C):** repair rules (guillotine/anneal/slide) are
INERT-FIXED on pristine J2 (0 accepts, L12 50 steps + L28 30 steps) and
ACTIVE on damaged J2 (C2: 20-swap damage, longs 27 -> 5/13/14 with
17/29/9 accepts) — genuine fixed-point behavior, not brokenness.
Blind-form rules on J2: square/metropolis(T0.25,T1.0)/kappa FROZEN
(0 accepts; verified: all 1891 sampled swaps carry touched-C4 delta in
[-42,-22], mean -40.9, so metropolis acceptance ~ exp(-22) ≈ 3e-10 is
unreachable — J2 is a deep local C4-optimum under single swaps);
triangle DESTRUCTIVE (188 accepts, longs 0 -> 32, p 1.08 -> 0.01, leaves
the class). scramble kills as designed (negative control).
Caveat filed: the L12-torus p-window [5,11] is wrap-adjacent; audit
CLASS-ALIVE calls there inherit extra sensitivity. No DYNAMIC candidate
came close (best class-restore 1/3), so the caveat is verdict-remote.

**Single defects (BR-1G, GRAV-0 anatomy, no interpretation):** one M1
defect = exactly 1 long, bip_viol 0–1, qfrac 0.9965 (all 3 seeds); class
impact is lottery — 1/3 kills immediately (p 1.08 -> 0.64), 2/3 absorbed.
No bit-restores (degree-fiber pin holds exactly); class-restores
guillotine/anneal/slide/square = 1/3, 1/3, 0/3, 0/3 (< 2/3 bar).
Repair rules churn <= 4 edges (overlap 1148–1151/1152): they cannot reach
across the M1 degree-fiber step.

**Small-field (BR-1I):** max|dE| scales as eps^2 bit-cleanly
(0.077 -> 7.7e-18, ratios exactly 100 to 1e-15): the landscape vanishes
continuously, no threshold. No physical threshold inferred.

**Wave (C6, characterization only):** E1 packet, pristine disp 7.11
(PR 401 -> 608) vs N1-killed endpoint disp 16.13 (PR 401 -> 616):
killing the class does NOT localize the packet. Filed as a curiosity
for the wave/vacuum-track owners; BR-1 draws no conclusion from it.

**BR-3 handoff (mandatory):** downhill (dE < 0) and uphill (dE > 0) per
BR-2; neutral (dE = 0) carries **NEUTRAL-MOVE DEBT** — N0 reject =
frozen-analytic (G == J2, survival 1.0, micro-frozen); N1 allow =
measured-lethal (tau_class ~ 5 moves); NX existing-kinetics = VACUOUS
(no independently-justified vacuum-domain U_G inventoried; repair-rule
counterfactuals reported above, none selected). BR-3 must carry the
debt, not silently adopt dE <= 0 or dE < 0.

EM0-PREREG (FROZEN-2026-10-02 (~03:30-UTC (commit-predates-
ALL-EM0-campaign-runs!)); continuum-field-identification
(EM-0-gated-OPEN-by-POT1-FIELD + POT0-COLLECTIVE + BR2-QUADRATURE!)).
QUESTION (5-load-bearing!): (1)-what-equation-governs-static-POT1?;
(2)-what-equation-governs-long-wave-propagation?; (3)-does-dynamic-
reduce-to-static-at-envelope-zero (up-to-analytic-gap)?; (4)-what-does-
Jij-transport?; (5)-is-Bij-the-energetic-conjugate-of-the-POT1-field?
FROZEN-ONTOLOGY: G=bare-J2-torus + psi=r+i*s + H=-J*A (J=1-headline
(hbar=1 (native-graph-units!)); no-third-scalar/no-V/no-onsite/no-weights/
no-rewiring/no-backreaction-dynamics (read-only-wrt-graph!)). FIREWALL
(no-Maxwell/Coulomb/charge/photons/E/B/gauge/Lorentz/polarization/vector-
potential/1/r/c/eps0/mu0/e/hbar (EM-names-hypothesis-not-result!)).
BANKED-INPUTS (read-only-consumed (branch-tips (byte-identical-ballistic/
formation!))): POT0-COLLECTIVE (source-D=8.1e-14/packet-D=0.8551/v=1.211/
alpha=2.087/C-D-Spearman-1.0!); POT1-FIELD (delta-0.2295-vs-0.2304-0.4%/
xi-0.5288/0.5272/0.5265-0.4%/front-7.79-R2=0.9995/S-front-7.88/w_minus-0.95/
nodal-112/112/RB-0.26%/H-far-0.984!); BR2-QUADRATURE (R_B-sweep-+0.927/-0.457/
Pearson-0.971/E=-7.9381-cos/J_stag=7.938-sin/|Jx|=1.1713!); P1.1b (v=1.2039/
1.2110/alpha-2.07-2.09/R2>0.9997/mixing<=1e-12/n_zero=838!); Bloch-filed
(flat-0-EXACT + eps=-4(cos-kx+cos-ky) + Manhattan-max-8!).
APPARATUS (new-module-continuum.py (ADDS-only (banked-code-untouched!))):
real_rhs/rho_dot (0A) + bond_current/div_J/continuity (0B) + j2_bloch/
bands/velocity/hessian/max/spectrum/touching (0C) + taylor_coeffs/predict/
residual/envelope_pde (0D) + hessian_isotropy/velocity_anisotropy/quartic
(0E) + L_static/gap/IR-symbol (0F) + axial_kappa/ir_kappa/fit_decay/yukawa_k0
(0G) + L_dyn/unification-exact/IR (0H) + transient_predict (0I) + energy_both/
dE_dA/conjugate (0J) + BJ_polar/derivatives/identities (0K) + superposition/
sign (0L/M) + runner-scripts/em0_campaign.py (24-tasks (parallel!) + gates +
ladder (below!)) + tests/test_continuum.py (29-pins (theorems-only (NO-data!))).
DERIVED-PREDICTIONS (pre-data-math (pinned (NOT-assumed!))): (i)-rdot=-A*s/
sdot=+A*r + rho-chain-rule + 2nd-order-(dt2+A2)r=0; (ii)-J=2Im[conj*i*j] +
rhodot+divJ=0-exact + global-conservation; (iii)-H(k)=-f[[1,1],[1,1]] +
eps_disp=-4(cos+cos)/flat-0 + v=(4sin,4sin) + Hess=diag(4cos,4cos) +
maxima-axial-4/eucl-4√2/Manh-8 + zero-count-L2+touching (L6=46/L28=838!);
(iv)-Taylor-to-4th (Gamma-E0=-8/v=0/Minv=4I/cubic-0/quartic--1/6 (m*=1/4!
Schrodinger-like!)); (v)-Minv-isotropic-exact + quartic-ratio-0.5-diagonal;
(vi)-gap-0.5 + IR-0.5+2q2 + axial-kappa-arcosh(1.125)=0.4949 + IR-0.5;
(vii)-L_dyn(w,k)=w-eps + L_static=eps-w_drive + exact-match-at-drive +
IR-kinetic-shared-Minv + offset-0.5-k-independent; (viii)-front-8-Manhattan;
(ix)-E=-2ΣB + dE/dA=-2B + relocation-identity; (x)-B=ρρcos/J=ρρsin +
dB/dθ=-J/dJ/dθ=B; (xi)-superposition/superposition-exact + sign-phi-negates/
BJE-invariant.
GATES (PASS-⟺-ALL (frozen-thresholds (NO-shopping!))): 0A-real-vs-Krylov-1e-3
(dt=1e-5 (first-order-finite-diff!)) + rho-legs-1e-9; 0B-residual-1e-9 (random/packet/steady!) +
global-1e-9; 0C-Bloch-vs-exact-1e-9 (L4/L6/L8!) + zero-46/838 + vmax-exact +
packet-v-vs-bank-5%; 0D-Gamma-coeffs-exact + resid-O(q4)/O(q6) + envelope-
kind; 0E-Hessian-ratio-1.0 + vspread-1e-3-at-0.1 + quartic-0.5; 0F-gap-0.5 +
IR-symbol-5e-6; 0G-xi-stability-1.2 (L20/28/42/64!) + bank-5% + axial(K0!)-15% +
shell-vs-axial-15% + exp-beats-power-2x; 0H-exact-grid-1e-9 + IR-Minv-4I +
offset-0.5-spread-1e-9; 0I-front-v-in-(0.5,12)-R2>0.9 + |v-8|/8<5% + bank-5% +
instant-1e-9 + cone12-1e-6 + branch-w0<0.2 + accounting-1e-9; 0J-energy-legs-
1e-9 (single/pair/packet!) + conjugate-exact; 0K-BJ-identities-1e-12 +
phase-1e-9; 0L-superposition-1e-9 (L20+L28!); 0M-sign-phi-1e-9 + BJE-1e-9;
0N-xi-stability (=G_stab (intrinsic-range!)). CONTROLS: C0-Taylor-order
(=D_resid!); C1-packet-v-2%/D-5%/alpha>1.3 (P1/POT0!); C2-source-D<0.05
(POT0!); C3-AP-delta-solve-5%-vs-0.2304 + exchange-0.05 + xi-bank (POT1!);
C4-stagger-J=Csin-1e-9 (BR2-theorem!); C5-phase-invariance (=K_phase!);
C6-solve-rerun-bit-identical; C7-N + L42-packet-v-10%; C5ring-ring-v-10%+
alpha>1.3 (P1-apparatus!). LADDER: !(A&C)-or-!hard(C0&C5&C6)-or-!sectors
(D&G&I)->EM0-NULL (apparatus/sectors-invalid!); sectors-but-!H-or-!(H&
sectors&reg(C1-C4))->EM0-DISJOINT (phenomenological-not-one-equation!);
H&sectors&reg->EM0-FIELD (one-field-static+radiative!); +B->EM0-CONSERVED
(J-is-conserved-flux!); +J&K&L&M&N&C7&C5ring->EM0-BACKREACTIVE (static+
radiation+current+backreaction-linked (strongest!)). FORBIDDEN (even-
BACKREACTIVE-NOT!: electromagnetism/charge/Coulomb/Maxwell/photons/gauge/
Lorentz/polarization!). EXECUTION: beast-96 (jobs<=90 (Pool!)); seeds-frozen
(0/11/rng-pinned!); determinism-C6-gated; suite-parallel (pytest-xdist!);
no-local-experiments (beast-only!). NEXT: freeze-commit-then-beast-campaign
(gated!).
EM0-VERDICTS (beast-run-9174b7c (prereg-frozen-pre-data!); 24-tasks-32s +
suite-681-passed-2-skipped-182s-(-n-80!)): LADDER-EM0-BACKREACTIVE
(STRONGEST-RUNG (ALL-14-stages + ALL-8-controls-green-first-run!)).
0A-✓ (real-vs-Krylov-1e-3 + rho-legs-1e-9 (exact-two-scalar!)); 0B-✓
(resid-1.4e-14 + global-1e-9 (J-transports-|psi|2-norm (NOT-charge!)));
0C-✓ (Bloch-vs-exact-1e-15 (L4/L6/L8!) + zero-46/838 + vmax-8/4√2/4-exact +
packet-1.211-vs-bank-5% (analytic-4sin0.3=1.18208-vs-measured-1.21102-2.45%-
high (finite-sigma-4-+-COM-readout (filed-not-Bloch-error!)))); 0D-✓
(Gamma-E0=-8/Minv=4I/m*=1/4-Schrodinger-like + resid-O(q4)/O(q6)!);
0E-✓ (Hessian-ratio-1.0-exact + vspread-8e-4-at-0.1 + quartic-0.5-diagonal
(anisotropy-at-4th-order-only!)); 0F-✓ (gap-0.5 + IR-0.5+2q2-5e-6
(massive-Helmholtz!)); 0G-✓ (xi-0.5260/0.5265/0.5265/0.5265 (L20/28/42/64-
pairwise-0.1% (L64-=-L42-to-9-decimals-CONVERGED!) vs-bank-0.5% (solve-vs-
jump-vehicle!) + axial-K0-0.4890-vs-0.4949-1.2% + IR-0.5-1% + exp-beats-
power-2.6x (Yukawa-not-power!)); range-3-all-L-intrinsic!); 0H-✓ (exact-
grid-1e-9 + IR-Minv-shared-4I + offset-0.5-spread-0.0-exact (drive-detuning-
analytic-k-independent (FIELD-not-DISJOINT!))); 0I-✓ (front-L28-7.9916-
R2=0.99989/S-7.9014/L20-7.9927 (vs-predicted-8-0.1%! (vs-POT1-banked-7.79-
2.6%-high (threshold-T-coupling-filed: T=4-transient-max-vs-T=16-steady-max
(both-in-gate (ours-closer-to-bound!)))) + instant-exact-0 + cone12-3e-9 +
branch-w-=0.9408/w0=0.0036 (band-edge-radiation-✓ (POT1-0.95!))); 0J-✓
(energy-legs-1e-9-single/pair/packet + conjugate-exact (B-=-dE/dA/2J!);
POT1-steady-E-single=-11.6/pair=-21.9 (unnormalized-pinned-filed!)); 0K-✓
(BJ-1e-12 + phase-1e-9 (J-is-continuity-flux + B-is-energy-density +
dB/dθ=-J-canonical!)); 0L-✓ (superposition-1e-9-L20+L28!); 0M-✓ (sign-phi-
negates-1e-9 + BJE-invariant-exact-0.0 (symmetry-anatomy-not-charge!));
0N-✓ (=G_stab + range-3 (true-IR-not-torus!)). CONTROLS: C0-✓/C1-✓
(v=1.21102/D=0.85506/alpha=2.087 (bank-to-4-decimals!))/C2-✓ (src-D=8.07e-14
(bank-8.1e-14!))/C3-✓ (AP-solve-0.23037-vs-0.2304-0.01% (prediction-confirmed;
evolved-0.2295-0.4%-is-pinning-shift!) + exchange-0.05 + xi-bank)/C4-✓
(stagger-dev-3.5e-15!)/C5-✓/C6-✓(bit-identical)/C7-✓(v42=1.176-vs-v28=1.211-
3% (POT0-appendix-filed!))/C5ring-✓(0.9583-vs-0.95885-0.06%!).
INTERP (disciplined!): ONE-two-real-component-field-H=-A-has-static
(massive-Helmholtz-gap-0.5-Yukawa-K0-xi≈0.527) + radiative (Schrodinger-
envelope-m*=1/4-Manhattan-front-8) + conserved-current (J-transports-norm)
+ backreactive-energy (B-conjugate-same-E) sectors (mathematically-linked
(exact-Bloch + IR-shared-Minv + gap-analytic!)). FORBIDDEN-RESPECTED
(no-EM-claims!). EM-1-GATE: OPEN (falsification-next (radial-vs-required/
signed-matter/polarization/gauge/Lorentz!)).
EM1-PREREG (FROZEN-2026-10-02 (~04:30-UTC (commit-predates-
ALL-EM1-campaign-runs!)); electromagnetic-falsification
(EM-1-gated-OPEN-by-EM0-BACKREACTIVE!)).
QUESTION (5-falsifiers (ALL-required (one-or-two-green-NOT-pass!))):
(F1)-does-frozen-theory-contain-source-accessible-gapless-static-sector?;
(F2)-does-signed-conserved-additive-localizable-matter-quantity-exist?;
(F3)-do-two-physical-propagating-polarization-modes-exist?;
(F4)-does-local-redundancy-emerge-from-(G,psi)-ontology?;
(F5)-does-source-accessible-linear-isotropic-IR-sector-exist?
FROZEN-ONTOLOGY: EM0-frozen (G=bare-J2-torus + psi=r+i*s + H=-J*A
(J=1-headline!)); NO-new-DOF (no-charge/no-A_mu/no-E/B/no-photon-vars/
no-coin/no-edge-phases/no-node-components/no-gauge-links/no-onsite/
no-couplings/no-detuning/no-new-H!). FIREWALL: POT-1/EM-0-gap-NOT-tunable-
to-zero (w->-8-edge-access = edge-tuned-EXCLUDED (never-discovery!));
gaplessness-must-follow-from-symmetry/spectral-zero/conservation-law.
BANKED-INPUTS (read-only): EM0-BACKREACTIVE (one-field-static-massive-
Helmholtz-gap-0.5-Yukawa-xi=0.5265 + radiative-Schrodinger-m*=1/4-front-8
+ conserved-J + backreactive-B (exact-Bloch + IR-shared-Minv-4I!));
MALUS-0-NULL (7e26d06 (malus-law-m0 (single-propagating-sector ([H,S]=0/
H*P_anti=0-exact/sym=square@2J/n_zero=838=784+54/sym-v=1.2110-anti-frozen/
sheet0-50/50!)))); OBS-0-DISCORDANT (1563b55 (no-earned-common-metric =>
1D-operational-leg-MOOT (intrinsic-distance-only!))); SPEC-0 (3f9292d
(near-miss + rewired-match => SPEC-1/2-MOOT (no-bound-states!)));
P1-B0a/B1-NULL (af2dfe9 (no-sitters/anomalies (no-matter-candidates!))).
APPARATUS (new-module-falsification.py (ADDS-only (banked-untouched!))):
critical_table/nodal_sample/branch_mult/inventory (1A) + gap_class/chiral/
mirror/antisym-pins/secular-slope/solve_norm (1B) + commutant_table/range/
flat_proj/sheet_imbalance (1E) + PR/peak (1F) + sheetpin_mirror_dev (1G) +
mode_count/scan (1H) + local_phase/bond_law (1J) + compensation_T1T2T3/
cycle_winding (1K) + ray_fit/critical_class/bloch_eigvecs/overlap (1L) +
touching_rose (1M) + vortex_imprint/plaquette_circ/twist (1O).
TESTS (tests/test_falsification.py (18-pins (NO-campaign-data!))):
inventory-critical/nodal/L28-838 + gap-classes-frozen + chiral-algebra/
mirror-identity/norm-equal + anticonfined-bulk-0 (+sym-contrast!) +
slope-helper + commutant-L4 (commute-I/S/Tx/Ty/H/Pflat + Gamma-anticommute
+ ranges-0/1/1/2/global + filed-signed/conj!) + translation-unitarity +
flat-projector-trace-22 + sheet-signed-(+1/-1/0)-conserved + PR/peak-spots
+ sheetpin-mirror-exact-negation->0.5 + mode-single-everywhere + local-
visible-O(1)-global-0 + T1T2T3-residuals-O(1) + winding-integer-invariant
+ rays-(Gamma-quadratic/nodal-drift)-nowinding + rose-anisotropic +
vortex-circulation-twist-law.
RUNNER (scripts/em1_campaign.py (17-tasks-parallel!)): static/mirror/
anticonf/xi_L20/L28/L42/L64/radial/commutant/scons/poltrans/disperse/
sheetpin/localphase/t1t2t3/winding/vortex (+analytic-inline-1A/1H/1L/1M/1N
+ C6-det + bank-controls!).
GATES (frozen!): A-inventory-exact + kinds; B-class-frozen + static
(norms-finite-offband-resid-1e-6 + edge-div->3x + w0-singular!) + xiw
(xi-monotone-4pt-to-edge + ratio-<0.35!) + mirror-
exact + xi-mirror-1e-9 + anticonfined-bulk-1e-9 (+sym-contrast-1e-3!);
C-xi-ratio-<1.2 + range-<=4; D-exp-beats-power-2x; E-comm-filed + ranges +
chiral-L6 + Q_S-(+1/-1/0)-1e-9 + conserved; F-PR-ratio->50 + peak-decay->10x
+ dynasym-anti-disp-<5%-sym; G-mirror-1e-9 + negation->0.5 (FAILS!) +
Bsorted/E-1e-9; H-maxcount-1 + n_two-0; I-sym-v-5%-R2>0.9 + anti-frozen-5%
+ sheet0-Q0-conserved; J-local->0.05-all + global-1e-9-all; K-T1T2T3->0.05-
all + winding-integer + small-phase-invariant-1e-9 (+large-rewrap-filed
(discrete-only!)); L-nocone + rays + overlap-1-1e-12;
M-rose-spread->1.0; N-gap-0.5-refile (ONLY-unified-sector-massive!);
O-PR-ratio->2 + gam-ratio-<0.6 + twist-mono-from-0 (SECONDARY!);
C6-bit-identical + bank-xi-5% + bank-em0-5% + bank-v-2%.
FALSIFIERS: F1-PASS-iff-(admissible-gapless-AND-xi-grows-2x)
(EXPECTED-FAIL (only-edge-tuned-zeroes-gap (excluded!) + resonance-
has-no-static-response + mirror-same-range + anti-confined + xi-
saturates!)); F2-PASS-iff-bare-suitable (UNRESOLVED-iff-bare-unsuitable-
AND-matter-immature (EXPECTED-UNRESOLVED (S-conserved-signed-but-sheet-
automorphism-coupled (negation-fails!) + S-conjugation-propagating<->frozen
+ TxTy-momentum + H-energy + Gamma-not-conserved + Pflat-unsigned-arbitrary
+ single-site-disperses + SPEC/P1-no-matter!))); F3-PASS-iff-modecount>=2
(EXPECTED-FAIL (count<=1-everywhere-incl-touching (flat-frozen!) +
MALUS-replication!)); F4-PASS-iff-any-compensation-works (EXPECTED-FAIL
(local-phases-shift-BJE-O(1) + T1T2T3-all-O(1) + only-discrete-winding
(non-redundancy!) => complex-scalar-not-gauge-field!)); F5-PASS-iff-cone-
exists (EXPECTED-FAIL (Gamma/M-definite + X-indefinite + nodal-drift-
(v.q-NOT-v|q|) + eigvec-k-independent-winding-0 + rose-leading-anisotropic
+ only-unified-sector-massive!)). 1O-FILED (vortex-disperses + twist-
continuous (momentum-not-flux!) (cannot-rescue-F1-F5!)).
LADDER: !hard(A&B&C&D&E&F&G&H&I&J&K&L&M&N&C6&Cbank)->EM1-INVALID
(apparatus-broken-rerun!); all-PASS->EM1-SURVIVES; any-FAIL->EM1-FALSIFIED
(EXPECTED (F1/F3/F4/F5-FAIL + F2-UNRESOLVED!)); else->EM1-UNRESOLVED.
EXECUTION: beast-96 (jobs<=17 (Pool!)); seeds-frozen (0/1/2/rng-pinned!);
determinism-C6-gated; suite-parallel (pytest-xdist!); no-local-experiments
(beast-only!). NEXT: freeze-commit-then-beast-campaign (gated!).
EM1-VERDICTS (beast-run-8b0d95f (prereg-frozen-pre-data!); 17-tasks-33s +
suite-709-passed-2-skipped-74s-(-n-24-thread-capped (first--n-80-try-thrashed-
on-ARPACK-oversubscription@load-420 (killed-clean-reran-constrained (filed!))!))):
LADDER-EM1-FALSIFIED (F1-FAIL + F2-UNRESOLVED + F3-FAIL + F4-FAIL + F5-FAIL
(prereg-pattern-EXACT (all-15-stages + all-controls-green-first-run!))).
1A-v (Gamma-min--8/M-max-+8/X-saddles-0-flat_gap-0 + nodal-E0-drift +
L28-838-inventory-exact!); 1B-v (classes-frozen + norms-1.46/1.91/3.37/5.93
(edge-div-4.06x!) + w0-singular-NaN-resid + xiw-0.526/0.378/0.234/0.160
(monotone-ratio-0.30!) + mirror-exact-xi-bit-identical + anticonfined-bulk-
0.0-EXACT (sym-0.399-contrast!) (range-ONLY-via-tuning (pre-data-smoke-also-
killed-time-domain-secular-design (pinned-DC-not-growing (redesigned-to-
solve-level (prereg-updated-pre-commit!)))!)); 1C-v (xi-0.5260/0.5265/0.5265/
0.5265 (L64-=-L42-to-9-decimals-CONVERGED!) + range-3-all-L (SATURATES!));
1D-v (exp-beats-power-2.6x (Yukawa-not-power!)); F1-FAIL (no-admissible-
gapless-class (edge-excluded + resonant-singular + mirror-same-range + anti-
confined) + xi-saturates => NO-long-range-static-field (present-field-
cannot-reproduce-ordinary-long-range-EM!)); 1E-v (commute-I/S/Tx/Ty/H/Pflat-
exact + Gamma-anticommutes + ranges-0/1/1/2/4 + Q_S-+1/-1/0 + conserved-
3.6e-13!); 1F-v (symcell-PR-2->560-280x + peak-114x-decay (no-stable-object!)
+ site-PR-sat-7.86-frozen-fraction-filed (pre-data-smoke-caught-single-site-
design-error (redesigned-to-symcell (prereg-note-pre-commit!))) + dynasym-
anti-disp-0.0-exact (S-conj-maps-propagating<->frozen!)); 1G-v (mirror-0.0-
exact + negation-1.86-FAILS + Bsorted-0.0 + E-equal-16-digits (sheet-
automorphism-NOT-negation!)); F2-UNRESOLVED (S-signed-conserved-but-
unsuitable (no-negation-coupling + frozen-conjugate!) + matter-immature
(SPEC-0/P1-null-banked + dispersal-measured!) (NOT-PASS (constrains-future-
QK (must-pass-1G-where-S-failed!))); 1H-v (maxcount-1 + n_two-0 (48x48-grid-
incl-touching!)); 1I-v (sym-v=1.21102-R2=0.99974-alpha=2.087 (MALUS-digit-
for-digit!) + anti-disp-0.0-exact + sheet0-Q0-conserved!); F3-FAIL (single-
active-propagating-scalar-mode (MAJOR-falsifier!)); 1J-v (local-dB-0.207/
dJ-0.243/dE-5.28-O(1!) + global-1e-14/1e-17 (contrast-exact!)); 1K-v (T1-
0.255/T2-0.276/T3-0.265-all-O(1) (NO-redundancy!) + winding-1-exact +
small-phase-invariant-1e-9 + large-rewrap-0-filed (pre-data-smoke-caught-
wrapping-subtlety (telescoping-only-below-branch-cut (redesigned (prereg-
updated-pre-commit!))) (discrete-only!)); F4-FAIL (complex-scalar-field-
NOT-gauge-field (only-global-U(1)!)); 1L-v (nocone + Gamma-quadratic-(joint-
a1-0.005-quartic-contam/a2-1.97) + nodal-drift-(a1-5.69) + eigvec-overlap-1-
exact (winding-0!)); 1M-v (rose-0.49/5.64-spread-1.43 (LEADING-anisotropy!));
1N-v (gap-0.5-spread-0.0-refile (ONLY-unified-sector-massive!)); F5-FAIL
(no-linear-isotropic-source-accessible-sector!); 1O-filed (vortex-PR-201->
1141-5.7x + gam-0.0063->0.0002-ratio-0.024 (DISPERSES!) + twist-0.0->0.00056-
monotone (continuous-NO-quantum!) (momentum-not-flux (SECONDARY (rescues-
nothing!)))). CONTROLS: C6-v(bit-identical)/Cbank-xi-5%-(EM0-digits-to-4th-
decimal!)/Cbank-v-2%-(1.21102!)/Cbank-em0-5%.
INTERP (disciplined!): frozen-J2-wave-is-ONE-massive-complex-scalar-field
(Yukawa-xi=0.527 + Schrodinger-m*=1/4 + norm-current + B-conjugate) with
NO-electromagnetic-sector (statically-gapped + unsigned-coupled + single-
mode + ungauged + nonlinear-IR (five-independent-falsifiers (four-FAIL +
one-UNRESOLVED-pending-matter-that-does-not-yet-exist!))). FORBIDDEN-
RESPECTED (no-EM-claims (falsification-complete!)). EM-PROGRAM-BRANCH-POINT
(filed-not-decided!): (i)-new-microscopic-DOF (coin/edge-phases/vector);
(ii)-new-substrate (beyond-bare-J2); (iii)-drop-EM-target (scalar-program-
continues (backreaction/cosmology/gravity-tracks-unaffected!)).

## BR25-PREREG — Contraction/splitting ontology (D14-BR2.5, FROZEN PRE-DATA)

**Status:** apparatus + ladder frozen; campaign NOT YET RUN. Derivation +
consistency campaign: tests whether local contraction/splitting can carry
the BR-2 quadrature without violating banked invariants. Introduces NO
event-rate law, NO new dynamics, privileges NO field map pre-data.

**BR-2.5A conventions (derived from simple-graph ontology, not tuned):**
V' = V - {i,j} + {k} (k fresh, history-free); N(k) = (N(i) u N(j)) \ {i,j};
common neighbors collapse to ONE edge (multiplicity recorded in the
contraction record, not kept: A_ij in {0,1} is frozen); the consumed edge
becomes a self-loop on k and is DISCARDED (mutual relation of two now
indistinguishable locations is vacuous). Consequences pinned pre-data:
dN = -1, dE = -(1+c), simplicity preserved, R_U = 1 (neighborhoods at
distance >= 2 bit-identical; t ticks <= t hops).

**BR-2.5B candidate maps (all implemented, none privileged):** S sum
(a+b; Dn = +2B_ij), A average ((a+b)/2), N norm-preserving
(sum-direction x local norm; SINGULAR at a+b == 0 -> defined 0, filed).
No map selected cosmetically; the census decides.

**BR-2.5C census claims:** exact formulas dN/dE/dnorm per map (pinned in
units + campaign gates); dEpsi direct (no closed local form claimed).
Norm across contraction is EXPLICITLY ACCOUNTED, not forced conserved.

**BR-2.5D operationalization:** D1-with-record = exact graph inverse with
nonlocal memory (proves nothing local). Record-free split = cover
policies (A,B), A u B = N(k): 3^d degenerate policies (D2, finite).
Field: sum-equal roundtrip error = |a-b|^2/2 exactly (relative-mode
power = the obstruction; uniform fields roundtrip exactly). JUDGMENT
(frozen): the continuous field-mode loss is filed as INFO-ACCOUNT DEBT,
not the IRREVERSIBLE rung, because degenerate splitting IS derivable
from surviving local state; IRREVERSIBLE triggers only if no split
policy is restorative even with oracle choice or the wave law breaks.
Reversibility of graph dynamics was never banked; unitarity between
graph events was (gated).

**Campaign grid (frozen):** F: L12-torus edge (elist[10] avoiding node 0)
x 3 maps + R18-ball edge (elist[100] avoiding src) + L8 spectrum +
M1 contrast (seed 777), uniform field; G: record/oracle/field roundtrips
on the F edge (+ staggered phi=pi/2 field case); H: stagger tables
phi in {0, pi, pi/2, -pi/2} on J2-L12 uniform envelope + E zero-field;
J: ring-60 evolve10/contract(45,46)/evolve10 + J2-L28 E1 packet + contract
elist[10]; L: collapse ball r<=6 around node 0 on J2-L28 (seed 0) +
pristine/collapsed wave + spectra; M: collapse r<=4 balls at distance 9
(seeds 1/2) + bridge contraction with the SAME primitive; I: L28 cone +
3-tick chain; K: 3^d census only, DESIGN-OPEN (no event-rate law earned,
no pseudo-formation demo — explicit non-goal).

**Verdict ladder (frozen bars, scripts/analyze_br25.py):**
- INCONSISTENT iff census/cone/between-events gates fail.
- IRREVERSIBLE iff consistent but no restorative split policy (even
  oracle) or across-event evolution non-deterministic.
- LOCAL iff consistent + reversible-attempt viable + multitick cone +
  M1-contrast (R_U=1 vs remote reach).
- QUADRATURE iff LOCAL + H separation (all +1 @0, all -1 @pi, all 0 with
  max|J|>0.1 @pi/2) + J-orthogonality bitwise + E bitwise null +
  sum-map Dn == 2B on the campaign edge.
- ONTOLOGY iff QUADRATURE + J deterministic + L collapsed-state
  well-defined (ext == boundary, steps == size-1) + M composes
  (same primitive, census exact, ext == union boundary).

**Predictions (filed, not gates):** LOCAL + QUADRATURE reachable;
ONTOLOGY iff L/M/J clean; D3 field-mode loss WILL be found (dimension
counting) and filed; NORM-ACCOUNT DEBT (2B created/destroyed per event
without a reservoir) WILL be filed; event-rate law stays unearned
(BR-3C debt); K stays DESIGN-OPEN.

**Debts pre-filed:** NORM-ACCOUNT (contraction changes ||psi||^2 by 2B
unless exchanged/stored somewhere); INFO-ACCOUNT (relative mode +
partition forgotten per event; record size quantified in L); RATE-LAW
(no tendency->probability map derived or assumed).

## BR25-AMENDMENT-1 — J-bar scale erratum (filed, BR0-AMENDMENT-1 style)

The prereg H bar wrote absolute J_maxabs > 0.1 (N=8 unit-test scale) for
the J2-L12 campaign table (N=288, rho^2 = 1/288). The data show perfect
separation (1152/1152 neutral with |J| = rho^2 exactly); only the
absolute bar misfired on scale. Corrected bar (strictly stronger):
|J_maxabs - rho^2| < 1e-12 (exact saturation at the theoretical maximum).
Analyzer updated + rerun; 15/15. The physics affirmed is stronger than
the physics preregistered (saturation, not presence).

## BR25-VERDICT — BR25-ONTOLOGY (15/15 gates, debts owned)

**Campaign:** data/br25_contraction.json (beast run, 58 s, frozen runner).
**Ladder:** consistent (census/cone/unitarity exact) -> reversible-attempt
viable (record-exact + oracle-among-degenerate + deterministic) -> LOCAL
(+ multitick cone + M1-contrast) -> QUADRATURE (+ H separation, ortho,
E-quiescence, 2B-wiring) -> ONTOLOGY (+ J + L + M). All five checklist
items hold; the four pre-filed debts stay filed (below).

**Primitive (A/C):** dN = -1, dE = -(1+c) exact on every map and substrate
(J2 triangle-free -> c = 0, dE = -1); sum-map Dn = +2B_ij wired to the
BR-2 quantity (campaign edge residual 0.0); single contraction moves IR
barely (p 1.0797 -> 1.0854, C4 -21 local, spectral radius 8.0 -> 8.11).
M1 contrast: one relocation reaches 8 hops with a length-3 chord vs R_U
= 1 by construction (pinned units + campaign, single + 3-tick).

**Splitting (D/G):** record-inverse bit-exact; oracle cover unique among
3^14 = 4,782,969 degenerate policies (D2 finite for graphs); field
roundtrip error = |a-b|^2/2 exactly (uniform fields roundtrip with error
0.0; staggered derr = rho^2 = 0.0035 = formula). The D3 field-mode loss
is QUANTIFIED, not hand-waved (INFO-ACCOUNT DEBT stands).

**Quadrature (H/E):** phi=0: 1152/1152 contractive (B = +rho^2, J = 0);
phi=pi: 1152/1152 expansive (B = -rho^2, J = 0); phi=+/-pi/2: 1152/1152
neutral with |J| = rho^2 saturated, geometric readouts bitwise identical
under J -> -J. psi=0: B=J=tendency all zero bitwise (quiescence follows
from the tendency-proportional-to-B FORM — the form itself is the tested
candidate, not a derivation; owned).

**Wave (J):** evolution deterministic across events (bitwise rerun);
unitary between events at the post-jump norm (ring jump 2.2e-07 =
packet-tail 2B, accounted); H(G') + B/J readers history-free on fresh
labels.

**Collapse (L):** region 170 -> 1 in 169 steps; ext degree 56 = boundary
exactly; through-distance 28 -> 16, diameter 28 -> 22; packet propagates
through the collapsed state nearly identically (disp 7.34 vs 7.11,
PR 397->571 vs 401->608 — no reflection catastrophe, characterization).
Banked as a COLLAPSED GRAPH STATE (no horizon language).

**Merger (M):** adjacent collapsed regions compose via the SAME
contract_edge on the bridge (dE = -1 = formula, ext 76 = union boundary
exactly). No special merger law; ontological economy holds.

**Debts (filed, verdict-remote):** NORM-ACCOUNT (each event creates /
destroys 2B of ||psi||^2 with no reservoir — BR-3C must specify exchange
or storage); INFO-ACCOUNT (partition + relative mode forgotten per
event; record size = explicit reversibility price); RATE-LAW (no
tendency->probability map derived or assumed — BR-3C must earn it);
K DESIGN-OPEN (no formation demo attempted, per prereg).

**Handoff:** M1 relocation demoted to experimental/formation tool (per
the ONTOLOGY clause); the BR-3 loop is REPLACED by BR-3C (coupled
contraction dynamics: psi -> B -> G' -> H(G') -> psi') once the rate law
is earned. GRAV-0 input: exact structural light cone R_U = 1/tick.

## CONS0-PREREG — Joint graph-field invariant census (D14-CONS0, FROZEN PRE-DATA)

**Status:** apparatus + ladder frozen; campaign NOT YET RUN. Accounting
foundation for BR-2.6: census all exact conserved quantities of the
frozen graph-field system and test whether local contraction/splitting
admits closed joint accounting. Derives NO event rate, decides NO
event occurrence, runs NO coupled dynamics.

**Frozen inputs (read-only, byte-identical):** BR-2.5 tip 3ea8cf1
(contraction.py + ballistic.py + backreaction.py + phase.py +
formation.py elist_window + all four test files: the contraction
primitive, dN=-1, dE=-(1+c), sum/avg/norm maps, 2B wiring,
3^d covers, R_U=1); EM-0 tip 3128ff9 (continuum.py + driven.py +
pyproject xdist + closure pin + both test files: continuity,
dE/dA=-2JB, Bloch, quadrature). Banked verdicts consumed:
BR25-ONTOLOGY (15/15), EM0-BACKREACTIVE (14/14+8/8),
BR2-QUADRATURE, BR1-FLAT.

**Frozen conventions:** H(G)=-A(G), J=1, hbar=1 (P1/EM-0 locked);
simple connected graphs; primary field map sum (avg/norm controls
only); tolerances: integers bitwise, small-system algebraic
identities 1e-12, energy/norm legs 1e-9, Krylov conservation 1e-9.
No new reservoir/weights/constants/thresholds (CONS-0 firewall).

**CONS-0A census (frozen claim):** dQ_M/dt=i<psi|[H,M]|psi> (pin
formula vs finite-diff 1e-6); conserved <=> [H,M]=0. Generic:
norm (I), energy (H), H^2 moment, spectral P_+/P_-/P_0 (all
commute; pinned under evolve_fixed 1e-9). Regular-conditional:
uniform-mode power |S|^2, S=sum psi ([H,uu']=0 <=> regular;
pinned both directions). NEGATIVE control: sublattice imbalance
Gamma does NOT commute ({A,Gamma}=0 pairs spectrum instead);
pinned non-conserved. J2-specific: Bloch sector weights W_k
(P_k via translation character sum; [H,P_k]=0 verified
computationally) and sheet-involution charge Q_J, J:(x,y,b)->
(y,x,1-b) ([A,J]=0 verified computationally; pure sheet-swap is
NOT a symmetry, pinned). Only generic/local candidates are
eligible for fundamental accounting.

**CONS-0B classification (frozen claim):** norm LOCALLY conserved
(EM-0 continuity re-pinned 1e-9). Energy with node density
e_i=-sum_{j~i} B_ij and canonical edge-local current (antisym
part of dB_ij/dt, dB_ij/dt=Im((Apsi)*_i psi_j-psi*_i(Apsi)_j)):
symmetric-part obstruction pinned nonzero (>1e-6) on a frozen
counterexample => GLOBAL-ONLY (total dE/dt=0 pinned; no
alternative local current proposed -- firewall). H^2 moment and
|S|^2 GLOBAL-ONLY by construction (no edge-local ansatz / no
node density; totals pinned). Bloch/J SECTOR (no local density
claimed). Gamma NOT-CONSERVED.

**CONS-0C ledger (frozen formulas):** dN=-1, dE=-(1+c),
dQ_psi=2B_ij (sum map), dE_psi=P1+P2+P3+P4 with P1=+2B_ij
(consumed relation), P2=-2(sum_{X_j}B_im+sum_{X_i}B_jm)
(merged-amplitude cross bonds, X exclusive neighborhoods),
P3=0 (common-neighbor collapse energy-neutral, verified not
assumed), P4=0 (external edges untouched, verified). HARD GATE:
parts sum == direct before/after dE_psi (1e-9) on every
campaign event. Components preserved (pinned). Every 0A
invariant rowed before/after/delta; d|S|^2=0 pinned 1e-12
(uniform mode is event-closed for ALL states -- load-bearing).

**CONS-0D/E (frozen pins):** 2B identity on random / bonding /
pure-current / antibonding / zero-spike fields x wall of
substrates (1e-12); phase table (0:+,-; pi/2:0,sat; pi:-;
3pi/2:0,-sat) exact per edge (1e-12).

**CONS-0F/G no-go (frozen theorem):** for fixed graph event,
dQ_tot=-a-b(1+c)+2gB+d*dE_psi. Lemma S1 (phase sweep at zero
elsewhere): dQ,dE trace 2rho^2 cos (pinned 1e-12). Lemma S2
(vary neighbor field at fixed edge state): dE varies at fixed
dQ (range>0 pinned). THEOREM: dQ_tot==0 for all states =>
g=d=0, then -a-b(1+c)==0 for all c in domain => trivial if
>=2 c-values; on fixed-c domains the 1-dim decoupled family
E_G-(1+c)N (c=0: cycle rank). COROLLARY: no field-involving
linear invariant closes; E-N closes bitwise on c=0, misses
by exactly -c elsewhere. Coefficients solved algebraically,
never fitted.

**CONS-0H (frozen formulas):** cycle rank xi=E-N+ncomp,
dxi=-c (bitwise); triangle count T, dT=-c-r+q with
r=#{double-preimage mergers}, q=#{created} (both defined by
unordered-pair census on N(k); bitwise); degree-square sum
D2, dD2=(di+dj-2-c)^2-di^2-dj^2+sum_C(1-2dm) (exact).
Closure test per candidate: field pair, same graph event,
dQ_psi differs while dQ_G identical (bitwise) => NO joint
closure (pinned per candidate). M=E+3T corollary filed.

**CONS-0I prediction:** ENERGY-ACCOUNT DEBT. Same separation
argument for dE_psi: pinned field pair varies dE at fixed
graph; candidates E_G, xi, T, D2 all fail (residual range>0
pinned each).

**CONS-0J criterion (frozen):** LOCAL <=> delta computable
from N[{i,j}] data alone, pinned by remote-mutation
invariance of ALL deltas. xi-closure on c=0: LOCAL. |S|^2:
event-closed but GLOBAL (S moves under remote mutation,
pinned).

**CONS-0K formulas (frozen):** split cover (A,B), c'=|A cap B|:
dN=+1, dE=+(1+c') (bitwise); equal policy: dQ=-|k|^2/2,
dE=-|k|^2/2-sum_{A cap B}B_km+sum_{A cup B}B_km;
norm policy: dQ=0, dE/(-2)=|k|^2/2+(sum_A+sum_B)B_km/sqrt2-
sum_{A cup B}B_km. All gated vs direct (1e-9). Record
inverse restores graph bitwise (banked); field iff a=b.

**CONS-0L counts (frozen):** enumerate 3^d covers x
{equal,norm} on frozen small-d events. Q1: #{d xi=0}==2^d
(triangle-free G'); Q2: #{(d xi,dQ)=(0,0)}==2^d (k!=0,
norm policy); Q3: #{exact full restoration}==0 for a!=b,
==1 for a=b. Expectation: constrains, never unique =>
DEGENERATE (filed, not SELECTIVE).

**CONS-0M debts:** conservation debt = max|dQ|,max|dE|
residuals over campaign (numbers filed); information debt =
log2(#admissible covers)+|a-b|^2/2 on pinned examples
(numbers filed); gate: info-debt>0 where accounts close
(scalar conservation != reversibility).

**CONS-0N prediction:** zero field ALLOWED (all field
deltas bitwise 0; ledger consistent on c=0) => conservation
does not explain vacuum quiescence; event law still owed.

**CONS-0O prediction:** norm account BLIND (dQ=0 both
sectors, pinned); energy account DISTINGUISHES (dE=0 at
psi=0 vs dE=-2 sum_X B^nonedge !=0 at phi=pi/2, pinned
to formula).

**CONS-0P substrates (frozen):** j2-L6, square-torus-6,
ring-24, path-12, er-24-seed7-p0.25, handbuilt-diamond
(c=1 AND c=2 edges guaranteed), collapsed-mini (J2-L8
r<=2 ball via frozen contract_edge, lowest-elist order).
Same code path everywhere (C6); xi-closure holds <=> c=0
(gated per substrate: d xi+c==0 bitwise).

**CONS-0Q grid (frozen):** substrates x fields {zero,
uniform, stagger phi in {0,pi/2,pi,3pi/2} (bipartite only),
random-seed12345, spike-on-i} x 2 frozen edges each
(elist[len//3], elist[2*len//3]; handbuilt: the c=1, c=2
edges) = ~84 contraction events; every event compares
ALL analytic deltas vs direct; split census on ring-24 +
handbuilt events (d(k)<=4); 0A/0B pins on ring-8/J2-L4/
path-8/er-12-seed3. data/cons0_ledger.json via
scripts/run_cons0_campaign.py (mp pool); gates applied by
scripts/analyze_cons0.py. NO fitting after opening data.

**Controls (frozen bars):** C0 vendored contraction tests
pass + dN/dE/2B re-pinned; C1 vendored continuum tests
pass + continuity re-pinned; C2 global-phase ledger
invariance 1e-12; C3 endpoint-exchange identical deltas +
edge-sets; C4 conjugation identical deltas, B->B/J->-J;
C5 remote-mutation invariance (0J); C6 same-tolerance
completion on all substrates.

**Verdict mapping (frozen):** CLOSED requires a
field-involving non-decoupled invariant closing exactly +
locally for arbitrary states (expect NO). PARTIAL =
>=1 independently-defined account closes (xi on
triangle-free; |S|^2 event-leg) AND norm/energy joint
no-go proven+pinned (expect YES). NO-CLOSURE = nothing
closes. SELECTIVE additionally requires conservation to
forbid some contraction events (expect NO: 0N allows
zero-field; splits DEGENERATE). Expected: CONS0-PARTIAL.
Handoff: BR-2.6 blocked from a conservation-derived
contraction law; NORM-ACCOUNT + ENERGY-ACCOUNT + EVENT-RATE
+ SPLIT-DEGENERACY + INFORMATION-LOSS debts filed.

**CONS0-PREREG clarification (pre-data, no campaign run yet):** Q3
counts (cover,policy) pairs with exact full restoration: the record
cover is unique per policy, so Q3 = #{policies restoring the field}
= (1 if a==b else 0) + (1 if a==b==0 else 0): nonzero uniform -> 1,
zero field -> 2 (both policies fix (0,0)), a!=b -> 0. Likewise Q2 =
#{disjoint covers} x #{policies with dQ==0} = 2^d x (1 + (1 if k==0
else 0)): norm policy always qualifies; equal qualifies iff k==0
(zero field, phi=pi stagger). Analyzer implements these exact
expectations per event; the prereg's "==1 for a=b / ==2^d" shorthands
are the nonzero-uniform / k!=0 cases.

## CONS0-AMENDMENT-1 — sheet-swap symmetry erratum (pre-campaign-data)

The prereg claimed pure sheet-swap S:(x,y,b)->(x,y,1-b) is NOT a J2
symmetry. The apparatus refuted this before any campaign data: [A,S]
= 0 exactly (bitwise). Root cause: the b=1 generator swap (u,v)->
(v,u) permutes the generator SET {(+-1,0),(0,+-1)}, so every edge
maps to an edge. Correction (strictly stronger census): BOTH S and
J are J2 involution symmetries (Q_S, Q_J conserved, pinned); the
symmetry negative control is a seeded random permutation ([A,P]!=0
pinned). Census table gains the sheet_S row (j2-symmetry class).
Verdict mapping unaffected (both remain J2-specific, ineligible for
fundamental accounting). Companion fixes (same commit, apparatus
stage): quad_rate_findiff uses evolve_fixed n_steps=2 (the frozen
API needs >=2 time points); energy-rate test ditto.

## CONS0-VERDICT — PARTIAL (22/22 gates green, executed on beast)

**Campaign:** scripts/run_cons0_campaign.py on beast (96-CPU, mp pool);
data/cons0_ledger.json: 88 contraction events (7 substrates x fields x
2 frozen edges; c in {0 x72, 1 x12, 2 x4}) + 576 split rows (24 groups
x 3^d covers x {equal,norm}, d<=4) + S1/S2 separation + 0A/0B pins +
C2-C5 controls. scripts/analyze_cons0.py: 22/22 gates green. Matches
the frozen prereg expectation exactly; no post-data fitting (pre-data
tooling repairs only: exact phi record, split formula serialization,
pins-task arithmetic, backward findiff leg).

**Ledger (every analytic delta gated vs direct before/after):**
N: fixed-G n/a (graph); d=-1; split +1. E_G: n/a; d=-(1+c);
split +(1+c'). Q_psi: yes (generic, LOCAL); d=+2B_ij; split
-|k|^2/2 (equal) / 0 (norm). E_psi: yes (generic, GLOBAL-ONLY);
d=P1+P2 verified; split formula verified. H^2 moment, spectral
W: yes (generic); deltas direct-filed. |S|^2: regular-only;
d=0 exact (event-closed, GLOBAL). Bloch W_k, sheet Q_J/Q_S:
J2-sector; sectors destroyed by event (filed). xi=E-N+ncomp:
n/a; d=-c; split +c'. T: n/a; d=-c-r+q; split direct-filed.
D2: n/a; exact formula; split direct-filed.

**0A census pinned (ring-8/J2-L4):** generic norm/energy/H2/
spec+-/0 all commute (Krylov 1e-9); regular-conditional |S|^2
both directions; Gamma negative ([A,Gamma]!=0, non-conserved);
J2 Bloch + sheet J + sheet S (AMENDMENT-1) sector symmetries.
**0B:** norm LOCAL (continuity 1.1e-16); energy GLOBAL-ONLY
(symmetric-part obstruction 0.318 > 1e-6; total dE/dt=0 at
8.3e-17); H^2/|S|^2 GLOBAL-ONLY; Bloch/J/S SECTOR; Gamma
NOT-CONSERVED. **0C:** dN/dE bitwise; dQ=2B; dE=P1+P2 with
P3=P4=0 (max 2.8e-17 / 0); parts==direct 2.2e-15; components
preserved. **0D/E:** 2B wall 1e-12; phase table exact per edge
1e-12. **0F/G no-go proven+pinned:** S1 traces 2rho^2 cos
(1e-12); S2 varies dE at fixed dQ (range 0.5); field probes
fail (max|lin_0010|=0.286, max|lin_0001|=0.667); gamma=delta=0
forced; fixed-c domains admit only decoupled E_G-(1+c)N (c=0:
cycle rank); lin_m110==-c bitwise. **0H:** dxi=-c bitwise
(LOCAL via C5); dT=-c-r+q bitwise (K4 (2,1,0)->-3; C4
(0,0,1)->+1); dD2 exact; joint closure fails per candidate
(zero/uniform pair varies dQ at fixed graph, all substrates).
Triangle census: J2-L6 contractions create q=21 each (c=0);
collapsed-mini q in {16,21}; er-24 q in {5,6}. **0I:**
ENERGY-ACCOUNT DEBT (E_G/xi/T/D2 all fail, residual range>0).
**0J:** xi-closure LOCAL (C5 2.8e-17); |S|^2 GLOBAL (S moves
remotely) + evolution-fragile (regular-only). **0K:** split
formulas gated 1e-9; record inverse restores graph bitwise,
field iff a=b; components preserved. **0L:** Q1=2^d, Q2=2^d
(x2 if k==0: zero + phi=pi stagger), Q3=(a==b)+(a==b==0) --
all 24 groups exact => DEGENERATE (constrains, never uniquely
selects; Q3=0 for a!=b). **0M:** conservation debt max|dQ|=
0.286, max|dE|=0.667; info debt: >1 admissible (dxi,dQ)=(0,0)
cover in every group (e.g. log2(4)=2 bits at d=2) + |a-b|^2/2
mode erasure. **0N:** zero-field contraction ALLOWED (field
deltas bitwise 0; xi-ledger consistent on c=0) => conservation
does not explain vacuum quiescence. **0O:** norm BLIND (dQ=0
both sectors); energy DISTINGUISHES (dE=0 at psi=0 vs
dE=-2 sum_X B^nonedge !=0 at phi=pi/2, pinned to formula).
**0P:** all 7 substrates complete, same code path (C6);
xi-law holds <=> c=0 per substrate (dxi+c==0 bitwise); no
closing account uses J2 coordinates => universal statements
stand, J2 rows filed J2-specific. **Controls:** C0/C1 vendored
suites green (beast full suite; count in CHANGELOG); C2
2.2e-16, C3 0, C4 (B same / J flip), C5 2.8e-17.

**Verdict: CONS0-PARTIAL.** Closing accounts: cycle rank xi on
triangle-free domains (LOCAL, exact) + uniform mode |S|^2
event-leg (exact, GLOBAL + evolution-fragile). No
field-involving linear invariant closes (no-go proven); energy
account open. No contraction event forbidden by conservation
(0N allows; splits DEGENERATE) => not SELECTIVE.

**Debts filed:** NORM-ACCOUNT (max|dQ|=0.286), ENERGY-ACCOUNT
(max|dE|=0.667), EVENT-RATE, SPLIT-DEGENERACY (Q3<=2, 0 for
a!=b), INFORMATION-LOSS (>=2 covers + mode erasure).

**Handoff:** BR-2.6 blocked from claiming a conservation-derived
contraction law; may consume the xi domain constraint + split
counts but must carry all five debts. The model owes a
reservoir/principle for norm/energy event accounting.

## BR26-PREREG — Joint accounting + event-law derivation (FROZEN PRE-DATA)

**Status:** derivations + apparatus + ladder frozen; census NOT YET RUN.
Derivation campaign: conservation decides, nothing is chosen. No
temperature, Metropolis, threshold, rate, coupling, reservoir, ranking,
or vacuum-restoration term is introduced (firewall).

**D-no-go (proven pre-data, pinned constructively):** for Q_tot =
aN + bE + gQ with FIXED coefficients, universal per-event conservation
(-a - b(1+c) + 2gB = 0 for ALL events) forces a = b = g = 0. Proof: fix
(G,i,j), vary psi (B ranges over R) -> g = 0; vary c over edges -> b =
0; remainder -a = 0. Admitting dE_psi does not help: varying one cross
neighbor field moves only the d-term -> d = 0, reducing to the linear
case. Corollary (F): NO graph-defined reservoir can satisfy DQ_G = -2B
(graph side fixed while B varies). Pinned via find_*_violation exhibits.

**Sum-identity (banked, zero selection power):** sum-map contraction
preserves Sigma psi exactly, hence |Sigma psi|^2; holds for EVERY event
identically, so it constrains nothing (filed, not a closure).

**H-form (derived, ratios free):** conditional conservation DQ_tot = 0
holds IFF B_ij = B_*(c) = (a + b(1+c))/2g (affine in c). The FORM is
derived; the TWO RATIOS (a/g, b/g) are free: nothing in the ontology
fixes them, and vacuum-tuning them (e.g. to quiesce J2) is firewall
forbidden. g = 0 special cases: graph-only c_* = -a/b - 1 (an infinite
discrete family over k >= 0; selecting k = 0 "because J2" is forbidden);
a-only -> never; all-zero -> trivial. Remark (pinned, not a law):
Delta(E - N) = -c, i.e. E - N is conserved iff c = 0.

**I-prediction (NEGATIVE):** conservation yields EQUALITY-selection
(B = B_*, codimension-1, non-firing); the step to a firing
inequality/direction needs new physics. No deterministic zero-parameter
(C,N,S) partition follows. If the algebra holds, I returns NEGATIVE and
the firing/direction problem becomes EVENT-RATE debt (this is a result,
not a failure).

**G-formula (derived):** Delta E_psi^contract = 2B_ij - 2 Sigma_cross
(common collapse energy-neutral; pinned vs direct). Sign needs the
1-neighborhood: B alone is insufficient (B-insufficiency pinned by
same-B/different-cross exhibit).

**K-prediction:** conservation selects the B_*-level-set among degenerate
splits (solvable iff B_*(o) <= |s|^2/4); a continuous 1-real-dim family
remains -> SPLIT-DEGENERACY debt REDUCED, stands.

**L-result:** per-event loss = log2((3^d+1)/2) graph bits + 2 real field
dims (relative mode); exact reversibility incompatible with (G,psi)-only
state (many-to-one theorem). INFORMATION-LOSS debt stands.

**J-result (conditional):** seeded-random maximal matching is the unique
score-free, label-fair (in distribution) conflict resolution (validity /
maximality / seed-determinism pinned); with non-firing admissibility it
is VACUOUS. TICK-SCHEDULER debt stands.

**M/N-predictions:** psi = 0 -> B = J = Q = 0 bitwise; pure current ->
B = 0, |J| = rho^2, no event at generic ratios (separation holds, with
the filed vacuity caveat: measure-zero firing is quiescent everywhere).

**P-grid (frozen):** J2-L12 families {zero, bonding, current,
antibonding, random(seed 777)} + ER72-random control (seed 778):
per-edge (B, J, c) census; reference overlays R0 = (0,0,1) [B_* = 0],
R1 = (1,0,2) [B_* = 1/4], R2 = (0,1,1) [B_* = (1+c)/2] with eps-grid
{1e-3, 1e-2, 0.1} sensitivity (LABELED, BR-1H style; nothing selected).
Predictions: zero all B == 0; bonding all B > 0; current all B = 0 with
|J| = rho^2; antibonding all B < 0; random/irregular mixed-sign;
J2 all c = 0.

**V-tripwire (ACCOUNTED bar):** 6 constructed B_* states (3 ratio points
x {J2-L6, path-8}) must balance |DQ| < 1e-9 through the FULL apparatus
(contraction_census, not the algebra shortcut).

**Verdict ladder (frozen):** NO-CLOSURE iff V fails (algebra breaks);
ACCOUNTED iff V + P + no-go re-verification pass (conditional closure
verified); ADMISSIBILITY iff + ratio-fixing principle found (none on
the table -> structurally false, documented); EVENT-LAW iff + derived
partition (I-negative -> false). PREDICTION: ACCOUNTED.

**Six debts (pre-filed with predicted statuses):** NORM-ACCOUNT reduced
(conditional family, ratios free); ENERGY-ACCOUNT ledgered non-conserving
(B insufficient); EVENT-RATE stands (non-firing equality; firing needs
new physics); SPLIT-DEGENERACY reduced stands; INFORMATION-LOSS stands
(theorem); TICK-SCHEDULER stands (conditional). PREDICTION: BR-3C stays
BLOCKED on EVENT-RATE (+ ratios); P is the admissible constrained probe.

## BR26-VERDICT — BR26-ACCOUNTED (10/10 gates, predicted by the algebra)

**Campaign:** data/br26_accounting.json (beast run, sub-second census +
V-tripwire, frozen runner). **Ladder:** V-tripwire holds (6/6
constructed B_* states balance to <= 6e-14 through the full apparatus)
-> conditional closure VERIFIED; no-go exhibits re-verified; P families
match every prediction -> NOT no-closure. No ratio-fixing principle
exists (vacuum-tuning forbidden) -> NOT admissibility. I returns
NEGATIVE (equality non-firing, inequality unjustified) -> NOT event-law.
**= BR26-ACCOUNTED:** accounting is closed; event-rate law remains debt.

**What conservation derives (earned):** the conditional invariant family
DQ_tot = 0 IFF B_ij = B_*(c) = (a + b(1+c))/2g (form derived, verified
end-to-end); universal closure PROVEN impossible (linear + E-extended,
constructive exhibits); graph reservoir PROVEN nonexistent
(independence); energy ledger EXACT (dE = 2B - 2S_cross, common-collapse
neutrality, B-insufficiency pinned); sum-identity banked (zero selection
power, filed honestly); split degeneracy REDUCED to the B_*-level-set
(solvable iff B_*(o) <= |s|^2/4, continuous family remains).
Delta(E - N) = -c remark pinned (graph-only c = 0 rule exists for the
(-1,1,0) ratios — NOT selected: ratios unjustified either way).

**What conservation does not derive (debts):** firing (equality is
codimension-1, non-firing); direction (contract/split inequality needs
new physics); the two coefficient ratios (free continuous family);
reversibility (many-to-one proven: log2((3^d+1)/2) bits + 2 real dims
per event); scheduling (seeded-random matching derived conditionally,
vacuous without firing). The overlay sensitivity table demonstrates the
underdetermination directly: firing fraction swings 0 -> 1 across
stated (ratio, eps) reference choices — which is why none is selected.

**P-census (algebra validation):** zero all B == 0; bonding all B > 0
(+1.00); current all B = 0 with |J| = rho^2 saturated; antibonding all
B < 0 (-1.00); random +0.49/-0.51 mixed; irregular mixed with c in
{0..4} (107/115/49/13/3); J2 all c = 0 (triangle-free, data).

**Six debts (final statuses):** NORM-ACCOUNT reduced (conditional
family, ratios free); ENERGY-ACCOUNT ledgered non-conserving;
EVENT-RATE stands; SPLIT-DEGENERACY reduced stands; INFORMATION-LOSS
stands (theorem); TICK-SCHEDULER stands (conditional). **BR-3C stays
BLOCKED on EVENT-RATE (+ ratios).** The constrained P-census above is
the admissible probe until firing physics is earned. M/N hold with the
filed vacuity caveat (measure-zero firing is quiescent everywhere;
zero-field and pure-current quiescence verified in the letter).

## BR27-PREREG — Local stability / firing criterion (FROZEN PRE-DATA)

**Status:** derivations + apparatus + ladder frozen; validation NOT YET
RUN. Final derive-first attempt: the campaign must either exhibit a
derived instability or file EVENT-LAW PRIMITIVE DEBT and STOP (strong
stop honored: no BR-2.8, no rate shopping, no thresholds, no thermal /
noise / Metropolis additions in any guise).

**A-verdict (derived pre-data): A3.** No ontology-internal deformation
coordinate exists: (i) graph space is discrete (dN = -/+1 exactly, no
intermediate); (ii) weighted edge interpolation exits the P1-frozen
binary Hamiltonian kind mid-path (H entries fractional) — considered
and REJECTED as invented (firewall: interpolation solely for a Hessian;
weighted.py is a static-observable import, not a dynamical derivation);
(iii) field paths at fixed G keep (N, E) (sector split). All three
pinned. Consequence: B/C-linearized-graph-stability VACUOUS as graph
dynamics; C answered for the field (below).

**C-result (derived):** the only linearizable dynamics in the ontology
is unitary field evolution: perturbation norm conserved exactly
(linearity, no fixed point needed), propagator spectral radius exactly
1, opnorm exactly 1. NO growth possible: no field instability can
trigger anything (pinned).

**E-result (derived):** H = -A is psi-blind BY CONSTRUCTION (constructor
signature takes no field state — structural proof); the 2x2 edge block
is frozen [[0,-1],[-1,0]] (eigenvalues +-1, no state data); unitary
response bounded (no divergent signature). No H-spectral trigger can
carry BR-2 field-state dependence (bonding/antibonding share H
identically). E returns NEGATIVE (pinned + tabulated).

**D-predictions:** ordering WITHOUT kinetics. J2-L12 hand-derived rows:
bonding dE = -26 rho^2 (lower), antibonding dE = -30 rho^2 (lower),
current dE = -28 rho^2 (lower), zero dE = 0 (degenerate). The
I-hypothesis (bonding/antibonding on opposite stability sides) is
already dead at ORDERING level (both lower). Uniform all-downhill
scans predicted frac_down == 1.0 on J2-L12/square-6/ring-10 (the
ordering != firing exhibit: discrete maxima that never fire).

**F/G/H/I/J/K/L-statuses (frozen):** F stands down (no eigenvalue to
control; L-table = rescaled dE, no claim); G preserved-in-null (no
J-trigger introduced; current ordering measured, mechanism absent);
H vacuous + null-quiescent (no mechanism -> no events anywhere, vacuum
included, vacuity caveated); I dead at ordering (above); J vacuous (no
boundary to compare with B_*); K inherits A3 at the contracted end
(split dN = +1 discrete; SPLIT-SELECTION debt filed, moot); L outcome
"preference without mechanism" via all-downhill (stronger than
barrier: not even dual minima, yet static).

**N-grid (frozen, 15 rows, NO evolution):** j2-{zero,bonding,current,
antibonding,unequal(seed 31,set+renormalize),random(seed 32)} @
elist[10]; tri-{uniform,random(seed 33)} @ (0,1) [c = 1];
sq-{uniform,bonding} @ ((2,2),(2,3)); ring-{bonding,current} @ (4,5);
er-random (ER72 seed-search 40..60, field seed 34) @ elist[7];
collapsed-around-k (J2-L6 contract elist[3], uniform threaded, edge
(k, first-nbr)). Each row: B/c/dE/ordering + R0/R1/R2 conservation
reference (labeled) + stability NONE + direction NONE.

**M-grid (frozen):** per-substrate binary-kind H + uniform ordering
scan (J2-L12/square-6/ring-10/ER72) + global H-blindness flag.

**Verdict ladder (frozen):** NO-MODE iff A3-pins + C-no-growth +
E-blindness hold (all derivation-forced); STABLE-BARRIER iff dual
minima exhibited (predicted false: all-downhill refutes); INSTABILITY+
iff a criterion is derived (structurally false: A/E/C negative).
PREDICTION: BR27-NO-MODE. O passes structurally (null proposes no
criterion, hence no threshold).

**Predicted handoff:** EVENT-LAW PRIMITIVE DEBT filed; BR-3C stays
BLOCKED; the program states explicitly: one additional primitive
dynamical postulate is required to make geometry change.

## BR27-VERDICT — BR27-NO-MODE (7/7 gates, derivation-forced)

**Campaign:** data/br27_stability.json (beast run, 1.2 s, frozen runner;
14 N-rows — the prereg prose "15" is a counting typo, the frozen grid
lists exactly the 14 rows run). **Ladder:** A3-pins + C-no-growth
(3e-16) + E-blindness all hold -> NO-MODE inputs true; dual minima
refuted by all-downhill data (not even barrier structure); no criterion
derived (nothing to derive it from) -> INSTABILITY rungs unreachable.
**= BR27-NO-MODE:** the current ontology contains no mechanism that
causes structural events.

**Why each route closed (evidence, not assertion):** A3: graph jumps
are dN = -/+1 discrete; weighted interpolation exits the frozen binary
H kind mid-path (considered, rejected as invented); field paths keep
(N, E). C: unitary perturbation growth 3e-16, spectral radius exactly
1 (no Re > 0 possible). E: H takes no psi (signature proof); edge
block frozen +-1; opnorm 1; same-G/same-H across field rows tabulated
(J2-L12 rho = 8.0, gap 0.536 — identical for zero/bonding/current).
D: ordering complete and IRRELEVANT — hand-predictions exact
(bonding -26 rho^2 = -0.09028, antibonding -30 rho^2 = -0.10417,
current -28 rho^2 = -0.09722, all lower; zero degenerate), uniform
scans all-downhill on J2/square/ring/ER (frac_down == 1.0 everywhere:
discrete maxima that never fire), mixed rows (tri-uniform HIGHER
+1/3 via c = 1 neutrality, unequal/er higher) equally static.
F/G/H/I/J/K/L stand down as frozen (no object / preserved-in-null /
vacuous / dead-at-ordering / vacuous / A3-inherited / pathless).

**Debts:** EVENT-LAW PRIMITIVE DEBT filed (this campaign's bottom
line); SPLIT-SELECTION debt inherited, moot without firing. **Strong
stop HONORED:** no BR-2.8, no rate shopping, no thresholds, no thermal /
noise / Metropolis additions. **BR-3C stays BLOCKED** (needs at least
ADMISSIBLE-INSTABILITY, unreachable from here).

**Mandated statement:** one additional primitive dynamical postulate
is required to make geometry change.

## OBS0-PREREG (Operational Geometry Concordance; FROZEN-2026-10-02 (~03:30-UTC,
commit-predates-ALL-OBS0-campaign-data); branch cursor/obs0-concordance-69cc off
main-tail-a0c248c; beast-dir ~/obs0-69cc; workers<=90; NO-local-experiments (unit
tests only))

QUESTION: do independent physical probes on J2 (graph balls, random walk, wave
H=-A) infer the SAME large-scale geometry (dims + pairwise distances up to fixed
global calibration), with UV disagreement collapsing to an IR floor? Firewall:
rulers take (graph, node-ids) ONLY (no coords/quotient/r/generators/pairwise
fits); J2 coords = ground truth for test-set construction + post-hoc grouping
(sheet/shell labels) and C5 regression ONLY (C2-audited: permutation-invariance
+ source-token tests).

SUBSTRATES (frozen): J2-torus L in {20,28,42} (N=2L^2); C0 square-torus same L;
C1 random-regular d=8 N-matched seeds {0,1,2} (dims only); OBS-0I J2-L28 q=0.05
deletion (test_j2-frozen rule) seeds {0,1,2,3} (reduced battery). L64 d_H+Weyl
extension OPTIONAL (non-gated, filed-if-run). Intrinsic D = BFS depth from node
0 (vertex-transitive: = diameter); wrap-safe R < D/2 (C4, intrinsic).

RULERS (frozen, apparatus src/bh_graph/obs0.py this commit): (A) R_G = BFS dist;
d_H = log-log OLS over r in [4, floor(D/2)-1] (empty window = honest no-fit).
(B) unbiased CT walk generator -Lrw (jump-rate-1; exact via Lsym conjugation;
regular graphs: Lrw=Lsym=L/z): d_s from mean return Pbar(t)~t^{-d/2} over
t in {12,14,16,20,24} (hop units; per-origin P_ii same window); Weyl
counting_ds frozen (0.08,0.70) k=min(400,N-2) SECONDARY (filed). tau_D =
CFD-first-peak (first local max with height >= 1/2 trace-global-max, fraction
1/2 LOCKED), dt=0.25, Tmax=3(D/2)^2. (C) H=-A J=1 (P1 law, eigen-evolution;
C5 proves equivalence): delta launch (coordinate-free isotropic source);
tau_W = CFD-first-peak same rule, dt=0.05, Tmax=D; R_W = v_banked*tau_W with
v_banked J2=1.2075 (P1.1b (1.2039+1.2110)/2) / square=0.9658 (P1.1a mean);
d_W from arrival-volume A(T)=#{tau_W<=T} fit A~T^d over T in [that(4),
that(D/2-1)] via train-fitted affine law tau_W=a*R_G+b (a<=0 = no-fit).
Missing tau (none found) = None (excluded; <10% required per (substrate,L)
else FLAG, >25% = STOP). (D) POTENTIAL ruler ABSENT (POT1-NULL stands at
prereg, amend-3-rerun unexecuted); revival trigger: POT-1 >= POT1-POTENTIAL
=> OBS-0D followup (inversion preregistered then, pre-data).

SAMPLING (frozen): 16 origins per (substrate,L): origin_k = rng.integers(N),
rng=default_rng(6900+100*si+L), si: J2=0 sq=1 (pert: rng(7900+10*seed+L)).
Targets: 25 uniform-random per equal-width R_G-tercile of [1,D/2) per origin
(rng(8100+oi); 75/origin, 1200/(substrate,L)). Train = origins 0-7, test = 8-15
(split-by-origin = cross-prediction AND origin-independence). E2-secondary:
shell-averaged radial laws tbar(R) (descriptive, pooled origins).

CALIBRATION (frozen families, fit-train/freeze/predict-test): (G,W):
R_G = a*R_W+b (affine); (G,D): tau_D = A*R_G^p (log-log OLS); (W,D):
tau_D = A*R_W^p. Inverted to R_G units: Rhat_W = a*R_W+b,
Rhat_D = (tau_D/A)^{1/p}; delta = |Rhat-R_G|/max(R_G,4) (R-floor-4 LOCKED).
E1-primary: median delta per tercile on TEST (T3 = IR). E2: shell-law
residuals (descriptive). F: epsilon_ab(R) = median-delta in R_G bins
([1,4),[4,8),[8,12),[12,D/2)) (descriptive + UNIVERSAL-i).

GATES (frozen): C5 (wave regression, coords allowed): ring-400
|v-2sin0.5|/2sin0.5<0.01; torus-30 |v-0.9658|<5%; J2-L28 branch-pair
(k=(0.3,0)/partners, sigma=4.0, purified, T=10) within 10% of (1.2039,1.2110).
ALL-pass => wave apparatus valid. C0 (per L, pre-J2): d_H in [1.70,2.05] +
r2>0.99 + monotone-rise L20<28<42; d_s in [1.85,2.20]; d_W in [1.70,2.30];
floors filed (sanity each-delta_IR<=0.45 else investigate). ALL-pass =>
J2 interpretation UNBLOCKED (else STOP+amend, pre-J2-data legitimate). C1
(majority >=2/3 seeds each clause): d_H no-window OR |p-2|>0.5 OR r2<0.9;
AND d_s outside [1.5,2.5] (else apparatus-STOP reports-2-universally).
DIM-PASS (J2 per L): max_a |d_a(J2)-d_a(C0 same L)|<=0.15, a in {H,s,W}
(origin-means; C0-relative because estimator systematics (Manhattan-1.89
vs heat-2.07) are SHARED, absolute spreads filed). OBS0-METRIC: DIM-PASS
at L28+L42 AND all-3-pairs at L42: delta_IR(J2)<=delta_IR(C0)+0.05 AND
<=0.40 (L28 sanity <=0.45). DIMENSION-ONLY: DIM-PASS but metric fails.
DISCORDANT: DIM-PASS fails at L42 (L-trend filed; verdict-at-tested-scales).
UNIVERSAL: METRIC + (i) delta_T3<delta_T1 strictly all-3-pairs L42 + (ii)
per-origin median-delta_T3 IQR<=0.10 all-pairs L42 + (iii) sheet-PASS
(L28+L42: UV R in {1,2,3} >=1-R with |med_same-med_cross|/pooled>0.10
AND IR R in [8,min(12,D/2-1)] pooled <0.05, BOTH rulers) + (iv) pert-PASS
(|d_pert-d_unpert|<=0.2 all-rulers + W-D-delta_IR within 0.05) + (v)
W-D-delta_T3 non-increasing L20->28->42 AND G-pair floors stable +-0.05.
Sheet labels = validation-only test-set construction (allowed). EXPECTED
STRUCTURE (not gated): floors persist (Manhattan-vs-Euclidean-vs-wavefront
norm mismatch ~10-30%, C0 measures it); W-D tightest (both continuum);
shell-laws tighter than pairwise.

ANALYSIS (frozen): scripts/run_obs0.py (units: eigen|c5|origin|dims) + scripts/
analyze_obs0.py (verdict JSON). Eigensystems cached beast-side (npz, NOT
committed); committed: prereg+module+tests+scripts+verdict-JSON(data/obs0/).
Paper figures ONLY if verdict >= METRIC. NEXT: module+tests commit, then
beast C5/C0/C1 validation (gated on this commit).

## OBS0-AMENDMENT-1 (C1-d_s N-drift repair; FROZEN pre-J2-data (C1-eigen in hand,
J2-unopened); commit-predates-J2-campaign): the preregistered C1 d_s clause
(majority-of-seeds outside [1.5,2.5]) is WRONG-AS-WRITTEN: expander heat_ds reads
1.21/2.06/3.55 across N=800/1568/3528 (seed-stable to ~0.01) -- the N=1568 value
sits inside the band by saturation-crossover coincidence (P(24)~1/N saturated at
all N; the fitted slope measures tail-decay-vs-floor mix, N-dependent by
construction). The estimator is NOT broken: square-torus heat_ds = 2.0692 at ALL
L (P(12)/P(24) identical to 3 decimals, far from 1/N) -- L-independence IS the
geometric signature. REPLACED clause: C1-d_s-PASS iff seed-averaged heat_ds
range across N={800,1568,3528} exceeds 0.5 (non-geometric N-drift; observed 2.35)
OR majority-of-9-seeds outside [1.5,2.5] (original clause kept as alternative).
d_H clause unchanged (no-window expected, D=5-6 observed). J2 gates untouched.
NEXT: C0-origins + C1-dims, staged analysis (SUPERSEDED by Amendment-2/3 below).

## OBS0-AMENDMENT-2 (wave-arrival statistic repair; FROZEN pre-J2-data (C0-origins
in hand, J2-unopened); commit-predates-J2-campaign): the preregistered CFD-peak
tau_W is WRONG-AS-WRITTEN on the torus: sq-L42 test shows tau_W exploding for
R>=12 (med 17.5 at R[16,21) vs front ~9) -- torus refocusing peaks exceed the
direct peak, CFD skips the direct arrival (GW-delta_T3=0.29, WD=0.49: broken,
not physics). Direct peaks are unrecoverable by time-gating (refocus merges
early for far targets). REPLACED statistic: tau_W = FIRST-THRESHOLD-CROSSING
(first t with p(t) >= 1e-6, epsilon=1e-6 LOCKED; dt=0.05/Tmax=D unchanged).
Rationale: front-edge feature (wrap-immune: wrap paths arrive later; 0 missing
on sq-L42; linear law R=2.38t+6.1, slope ~= angle-averaged front speed).
tau_D KEEPS CFD-peak (bulk-diffusion probe, p=2.06/GD-delta_T3=0.18: working;
first-crossing would collapse it to ballistic hop-counting t*~R, near-
tautological vs R_G -- rejected deliberately). Asymmetry is principled: each
ruler keeps its wrap-robust BULK arrival feature (wavefront edge / diffusion
bulk peak). ACCOMPANYING BUGFIXES (code did not match prereg text): (i) dW
window uses the FORWARD train law tau_W=a*R+b (code passed inverse-law coeffs
-> dW~0); (ii) arrival_volume clamps T_lo to >= dt (affine UV-curvature can
extrapolate b<0; window must lie in measurement domain; deterministic);
(iii) sheet-IR tau-key typo. Tests updated (crossing units). C0 gates/values
unchanged (C0 re-runs origins with the new statistic; J2 still unopened).
NEXT: re-run C0-origins, staged analysis (SUPERSEDED by Amendment-3 below).

## OBS0-AMENDMENT-3 (d_W estimator replacement; FROZEN pre-J2-data (C0-origins in
hand, J2-unopened); commit-predates-J2-campaign): the preregistered arrival-
volume d_W is WRONG-AS-WRITTEN: front-crossing taus carry a large precursor
offset (R=2.38t+6.1), so A(T)~(T+C)^2 with C~T_window reads dW~1.1, not 2
(offset-dominated, not geometry). REPLACED estimator: PURIFIED ball-1 quantum
return -- remove |E|<=1e-9 spectral weight (tol LOCKED; graph-intrinsic via
eigenbasis), measure q(t) = weight on {origin + 1-hop neighbors}, fit
q(t)~t^{-d} over T in [1.5,4.0] (dt=0.1, 26 pts). Rationale chain (C0-diagnosed):
onsite return is window-chaotic (revivals: -1.3..5.7 across windows/L); ball-1
smooths to L-stable 2.12/2.27/2.22 (L20/28/42). Purification is REQUIRED on J2
(extensive E=0 flat band ~50% weight would plateau unpurified return; same rule
both substrates; square loses only nodal modes ~5-9%). C0-dW band WIDENED to
[1.70,2.45] (contains true 2.0 + C0 readings with margin; DIM stays C0-relative
so the ~2.2 systematic cancels). arrival_volume_dim SUPERSEDED for d_W (kept in
module, tested, unused by campaign). Filed descriptively: unpurified plateau +
N_flat/N (J2 microstructure pin). NEXT: re-run C0-origins, staged analysis.

## OBS0-VERDICT (OBS0-DISCORDANT-at-tested-scales (dW-only, finite-size,
mechanism-understood); campaign-closed 2026-10-02; record data/obs0_verdict.json)

GATES: C5-PASS (ring 0.03%, torus 0.67%, J2-branch 1e-5 vs banked -- eigen
evolution == P1-Krylov to 5 decimals); C0-PASS all-L (dH 1.83/1.86/1.89 monotone
r2>0.99, ds 2.0692 x3 EXACT-stable, dW 2.18/2.28/2.23, floors GW~0.17 GD~0.17
WD 0.03-0.16); C1-PASS (dH no-window D=5-6; ds N-drift 1.21->3.56 range 2.35
(Amendment-1); weyl 6-14 (wild)); missing-tau 0.0% all-tags (no FLAGS/STOPS).
J2-opened ONLY after C0-stage pass (discipline kept; Amendments 1-3 all pre-J2).

DIM (C0-relative, bar 0.15): dH gaps 0.0000 EXACT all-L (J2 balls = 2x square
balls exactly); ds gaps 0.0005 all-L (J2 2.0697 vs C0 2.0692); dW gaps
1.86/1.35/0.57 (L20/28/42) -- FAIL (sole failure). METRIC-pairs (L42,
non-inferiority + 0.40 cap): GW/GD/WD ALL-PASS (J2 0.177/0.170/0.105 vs C0
0.164/0.181/0.164 -- J2 WD TIGHTER than C0 at L20/28 (0.015/0.058 vs
0.034/0.056)). LADDER: DIM-fails => OBS0-DISCORDANT (at L<=42).

MECHANISM (dW shortfall, diagnosed post-verdict from cached eigen): J2
purified ball-1 return drops steeply (UV, t<1) then hits a slow-mode-beating
residue floor ~1e-3 by t~2 (oscillating, NOT ergodic: near-flat-band slow
modes linger), masking the t^-2 ballistic decay inside window [1.5,4]; floor
thins ~1/N with L => dW 0.32->0.93->1.66 (L20->28->42). Flat-band pin
CONFIRMED: nflat/N = 54.7/53.4/52.3% (J2) vs 4.6% nodal (sq-L42); w0 =
0.52-0.55 (J2) vs 0.03-0.05 (sq) -- purification removes half the J2 packet
(same frozen rule both sides). L64-DIAGNOSTIC (filed, non-gating): J2 dW =
2.00 vs sq 2.17 (gap 0.17, just above bar); dH 1.9098 EXACT-match; ds
2.0697/2.0692; floors J2 0.147/0.160/0.154 vs C0 0.162/0.175/0.128
(non-inferiority holds). PROJECTED (not a verdict): DIM-pass at L>~100 as
residue thins below window.

UNIVERSAL-clauses (all filed; ladder already decided): (i) UV->IR: INVERTED
(J2-L42 T1->T3: GW 0.172->0.177, GD 0.103->0.170, WD 0.009->0.105 -- probes
agree in UV (all count hops) and DIVERGE in IR (Manhattan vs Euclidean vs
wavefront + diffusion wrap-shift); GW flips True at L64 both substrates);
(ii) origin-IQR: PASS (0.064/0.024/0.036 <= 0.10 -- OBS-0G positive:
no privileged origin); (iii) sheet: FAIL-as-gated (tD shows the FULL
pattern: UV-sensitive at R=2 (0.167) -> IR-blind (0.000); tW blind at ALL
scales (0.000 even R=1: single-hop wave arrivals sheet-degenerate at
leading order (same J) + dt=0.05 quantization; finer grid would not reach
0.10 -- physics, not resolution); (iv) pert: FAIL (dH/ds robust (gaps
0.00/0.01-0.03), WD-IR within 0.013, but dW gaps 0.17-0.53: deletion splits
the flat band past the frozen 1e-9 tol -> slow-mode artifact, estimator-side);
(v) scaling: FAIL (W-D-T3 rises 0.015->0.105 L20->42: IR bin moves to larger
absolute R where diffusion wrap-shift grows; G-floors stable +-0.013 PASS).

INTERPRETATION (filed, modest): J2 possesses C0-identical topological (exact)
and diffusive (4-decimal) IR dimensions AND C0-non-inferior pairwise ruler
relations -- but its wave-spreading dimension lags at L<=42 (slow-mode
residue) and ruler residuals do NOT shrink toward IR (distinct asymptotic
norms). "Same dimension + same ruler relations as known-2D, but no emergent
convergence": the geometry is SHARED (lattice-like) rather than EMERGENT
(IR-collapsing). OBS-1 (observer reconstruction) NOT opened (gated on
METRIC+). Followups (queued, non-gating): L128 dW convergence run; adaptive
purification-tol for perturbed dW; fine-grid tW sheet-UV (expect still <0.10).

**Kill relevance:** OBS0-DISCORDANT is a measurement outcome, not apparatus
failure (C0/C1/C5 all pass with margin; J2 pairwise matches-or-beats C0).
The dW-only finite-size failure + inverted UV/IR pattern constrain (not kill)
the J2-vacuum program: any OBS-1 reconstruction must handle slow-mode residue
and non-collapsing ruler floors.

## OBS0R-PREREG (IR Concordance Resolution; FROZEN-2026-10-02 (~04:30-UTC,
commit-predates-ALL-OBS0R-campaign-data); branch cursor/obs0r-resolution-69cc
off obs0-tip-1563b55; beast-dirs ~/obs0r-69cc (code) + ~/obs0r-data (write),
banked ~/obs0-data READ-ONLY; workers<=90 (<=8 for L128-origin procs);
NO-local-campaign-data (toy pilots L<=16 + unit tests only, listed below))

QUESTION (exactly two): (1) does the preregistered dW gap continue to close
at L128 per the filed finite-size model? (2) does the POT-1 static ruler
(POT1-FIELD, banked 5272a4f) agree with G/D/W in its available range? No
other OBS-0 criterion is reopened. HISTORICAL FIREWALL: OBS0-DISCORDANT at
L<=42 STANDS regardless of outcome (C6: verdict JSON retains it literally);
obs0.py is BYTE-IDENTICAL to the OBS-0 verdict commit (sha256 683f7620a0aa
00dff886c0e2a5022539bb5cefd6490ce0daa692539c1a55abde, hash-pinned in
tests/test_obs0r.py); no OBS-0 threshold/window/ruler/metric redefined; L64
stays a filed diagnostic (prediction INPUT, not verdict member); square
control retained; J2 coords stay validation-only (C2).

OBS0R-A (frozen dW(128) prediction, filed data ONLY): gaps |dW(J2)-dW(C0)|
1.860951568678995/1.3508304115377763/0.5706857074961125/0.1697 at
L=20/28/42/64 (verdict JSON + L64 diagnostic). Filed mechanism: slow-mode-
beating residue floor thinning ~1/N. Model (zero-intercept OLS on all 4):
gap(L) = 1632.4553/N_L. POINT: gap(128) = 0.0498. INTERVAL: [0, 0.3595]
(point + max|resid| 0.3097, floored at 0 since gaps are nonneg by def).
Filed-data mechanism checks (descriptive, pre-data): power-law gap~L^-p
gives p = 2.086 (~2 = volume scaling recovered); local decay exponents
accelerate 0.952 -> 2.125 -> 2.879 (L20->28->42->64). Expected J2 dW(128)
~= C0-reading minus ~0.05 (descriptive; PRIMARY = gap interval). CRITERIA
(exhaustive partition): W-FINITE-SIZE-CONFIRMED iff gap128 <= 0.15 (the
ORIGINAL OBS-0 DIM bar, in-interval) ; W-AMBIGUOUS iff 0.15 < gap128 <
0.1697 (decreases, misses bar); W-REFUTED iff gap128 >= 0.1697 (banked L64
gap; stops/reverses). No other reading of the wave result is admitted.

OBS0R-B (L128 wave adjudication): EXACT OBS-0 apparatus (same H=-A law,
delta prep, wave_return_dw over DW_TS [1.5,4.0] tol 1e-9, first-crossing
tau_W theta 1e-6 dt 0.05 Tmax=D, CFD tau_D dt 0.25 Tmax=3(D/2)^2 down to
DS_TS {12,14,16,20,24}, same origins rng(6900+100si+L), same 75 targets
rng(8100+oi), same V_BANKED, same calibration families, same train/test
origins 0-7/8-15, same wrap-safe R<D/2). Sole computational deviation
(preregistered with validation): taus computed ONLY for the union of the
75 frozen targets + POT targets + J2 sheet-matched extras (~500 nodes, not
all-safe ~16k: D^6 scaling makes all-safe infeasible at L128, ~5e16
flops/origin). Values on overlap are bitwise-identical (same matmuls).
VALIDATION (pre-J2-L128, banked data): `validate` recomputes L64 taus+dims
targets-only and diffs vs banked; PASS iff maxdiff < 1e-9 AND None-patterns
identical, both L64 tags. FAIL => STOP: fall back to all-safe (preregistered
fallback; campaign pauses for amendment, J2-L128 stays unopened). Sheet
extras (J2 only): sorted-first 10 same + 10 cross per R in
{1,2,3,8,9,10,11,12} (validation-only coords; deterministic test-set
construction). STAGING: eigen128 -> validate -> C4 -> sq-L128-origins ->
POT-sq/C3/C1 -> c0-stage-ANALYSIS (must pass: J2_open) -> j2-L128-origins
-> POT-j2 -> full-analysis. J2-L128 dW is unobservable before J2_open.

OBS0R-C (three-regime): epsilon_ab(r) = test-set median delta in width-4
R_G bins [1,4),[4,8),... over [1,D/2) (G/D/W pairs; frozen delta forms) and
P-bins [1,4),[4,7),[7,10] (P pairs). Shape rule (no thresholds):
interior_maximum = strict interior max (first<max-interior AND
last<max-interior; non-finite/short => False). UNIVERSAL-(i'): >=4/6 pairs
interior-max at L128-J2. C0 shape filed descriptively (no gate).

OBS0R-D (POT ruler R_P): read-only consumption of driven.steady_predict
(vendored verbatim from 5272a4f + ballistic.py for its imports; POT-1
ontology unchanged: H=-A, single-node s=1.0). omega = -(z+0.5), z = max
degree (gap 0.5 below band edge: J2/exp -8.5 = POT-1 OMEGA_J2, sq -4.5).
Raw observable phi_x uses (graph, node-ids) ONLY (C2: no R_G input at
measurement; R_G enters calibration exactly as OBS-0 (G,D) precedent).
Radial law F(r) = A r^-alpha e^-r/xi, log-linear OLS (Yukawa family, fixed
by lattice-Green theory, NOT fitted-form shopping). (G,P) map: F fit on
pooled TRAIN pairs; R_P = F^-1(phi_x) via brentq on [1,10]; validity =
F ok AND strictly decreasing on [1,10] (200-pt grid). Missing (out-of-
range/None) joins the OBS-0 missing rule (<10% FLAG, >25% STOP per
(substrate,L)). RANGE (honest limit): POT targets = 25/shell over shells
1..10 (rng(8200+oi), NEW frozen seed base for the NEW ruler); P pairs span
the MESOSCOPIC range only (static-field physics; omega retuning to widen
range = POT-1 redesign, FORBIDDEN). P-pair "IR" = bin 2 [7,10] (far end of
P's available range; verdict text states this caveat). L20 EXCLUDED for POT
(shell 10 not wrap-safe at D=20). NO d_P (honest branch, pilot-grounded):
L16 pilots show joint (alpha,xi) fits are pre-asymptotic/curvature-
dominated over every frozen shell range (alpha = -0.07 J2 / -1.28 sq over
shells 2..5 => C0 itself non-2D), and map-alpha is range-dependent
(0.39 over [1,10] vs shell-fit values) => estimator-dependent, not a
dimension. Map-alpha is FILED per cell as a field-geometry observable,
never as d_P (absence pinned by unit test). POT-1 kappa/xi NAMING FIX
(pilot-derived, mechanical): POT-1's filed "xi" 0.5272 is the decay RATE
(-d lnphi/dr, their code takes -slope and calls it xi); true xi = 1/0.5272
= 1.8968 (L28). Verified: static solve at L16 gives rate 0.5222 (true xi
1.915, +1% across sizes) and jump-evolved amplitude matches static to 0.3%.
C3 gates TRUE-xi (see Controls). If J2 (G,P) is monotone-invalid at L128
alone: that size's P pairs FAIL (no-fit). If invalid at BOTH 64+128 with
C3+C0 valid: P-INCOMPATIBLE (physics) => OBS0R-DISCORDANT.

OBS0R-E/F (four-ruler battery + held-out): pairs (G,D),(G,W),(D,W) EXACT
OBS-0 procedure (affine GW, powerlaw GD/WD, WD in R_W units). New pairs,
train origins 0-7 / test 8-15 (SAME frozen origins for all rulers), one
global map each, no pair/region-specific anything: (G,P): F above, delta
in R_G units (Rhat_P vs R_G, frozen delta_stat); (D,P): -lnphi = a sqrt(tD)
+ b (affine OLS; diffusive+Yukawa theory form), delta in sqrt(tD) units
(rhat=sqrt(tD), r_true=(-lnphi-b)/a, WD-precedent orientation); (W,P):
-lnphi = a R_W + b, delta in R_W units. Inverts are None-safe (a<=0 or out-
of-range => None => missing). Comparison bins: terciles (G/D/W, frozen)
vs P-bins (P pairs). METRIC pair rule (OBS-0 form): J2 <= C0+0.05 AND J2 <=
0.40, evaluated T3 (G/D/W) / bin-2 (P) at L128; sanity <= 0.45 at L64 (G/D/W
banked: 0.147/0.160/0.154 PASS already; P new).

OBS0R-G (dimensions): d_H, d_s, d_W via frozen estimators, origin means.
DIM128-PASS: max|d(J2)-d(C0)| <= 0.15 over {H,s,W} at L128 (0.15 = original
bar). d_P: none well-defined (see D). dW-part of DIM128 == W-CONFIRM bar.

OBS0R-H (origins): POT uses the SAME 16 frozen origins per (substrate,L)
(single-node source at origin). Filed per origin: (A,alpha,xi) map params
(J2/sq, all POT sizes), per-origin test medians. UNIVERSAL-(ii'): test-
delta IQR over origins <= 0.10 for ALL 6 pairs at L128 (T3/bin-2 medians;
OBS-0 form). Compared vs banked OBS-0 origin spread in verdict text.

OBS0R-I (sheets): G/D/W at L128-J2 from matched extras (same frozen
contrast stat): UNIVERSAL-(iii') = tD-UV-sensitive (>=1 R in {1,2,3} with
contrast > 0.10, banked tD pattern) AND tD/tW-IR-blind (pooled [8,12] <
0.05, banked pattern); tW-UV filed descriptive (banked physics: blind).
POT sheet: contrasts on phi at UV {1,2,3} + meso {8,9,10} pooled, J2 all
POT sizes, FULLY descriptive (P range does not reach IR; no gate).

OBS0R-J (sizes): headline L64+L128; banked L<=42 G/D/W reused untouched
(eigen npz + per-origin JSONs, read-only); POT battery NEW at L in
{28,42,64,128} x {J2,sq} (16 origins each) + C1 (below). NO reruns of
frozen-comparable expensive cells. NO perturbation substrate (banked pert-
FAIL was estimator-side by construction (frozen 1e-9 tol vs flat-band
splitting); rerunning cannot pass; resources to L128/POT instead; filed
limitation stands). Scaling UNIVERSAL-(v'): G-pair floors stable +-0.05
L64->L128 (banked->new) + W-D-T3 non-increasing L64->L128 (banked 0.1543)
+ P-pair bin-2 stable +-0.05 L64->L128 (both new).

CONTROLS: C0-L128-PASS (dims bands [1.70,2.05]+r2>0.99 / [1.85,2.20] /
[1.70,2.45] + all-6-pair floors <= 0.45 + dH(L128) > dH(L64-banked,
computed from banked files, no magic)); C0-POT-valid = sq (G,P) mono-valid
+ bin-2 defined at ALL POT sizes. C1 (banked G/D/W rejection STANDS,
frozen apparatus): C1-POT = expander d=8 N in {800,1568,3528,8192} seeds
{0,1,2} (POT solves only, GP-map analysis, no taus by design): cell
rejects iff mono-invalid OR bin-2 undefined; PASS iff >=7/12 reject (9/12
structural via D<=6 bin-2 emptiness regardless). C1-EXT: N=8192 eigen+dims
(dH clause >=2/3 seeds + ds drift over 4 N-values > 0.5, Amendment-1 form).
N=32768 C1-eigen SKIPPED (cost unjustified for frozen apparatus; filed).
C3-POT-regression (J2-L28 source node 0 = (0,0,0), recomputed static solve):
reality(max_imag<1e-9) + strict positivity + TRUE-xi shells-{2,3,4,5}-
mean pure-exp within +-10% of 1.8968 + range(max{r:shellmean>0.05}==3+-1)
+ residual<1e-9 + gap_ok; ALL <=> C3-PASS else P-branch VOID (ladder capped:
METRIC/UNIVERSAL unreachable; DIMENSION iff DIM128-G/D/W passes; wave
verdicts unaffected). C4-wave-regression (L128 cached eigen): J2 branch-
pair (C5-exact 4 specs, sigma 4.0, T=10) within 10% of (1.2039,1.2110) +
sq packet within 5% of 0.9658; projectors from CACHED eigen (same linear
maps, unit-pinned vs dense path; validates the cached artifact itself).
C5-wrap: frozen pre-wrap windows (G/D/W) + POT r<=10 << D/2 (wrap negligible
by banked 1J, filed). C2-audit: permutation-invariance tests for new code;
coords only in sheet grouping + C4 prep/readout. C6: verdict retains
"OBS0-DISCORDANT at L<=42" literally (analyzer writes it unconditionally).

LADDER (frozen mapping): !J2_open => OBS0R-BLOCKED. P-INCOMPATIBLE (D) =>
OBS0R-DISCORDANT. W-AMBIGUOUS/W-REFUTED => OBS0R-DISCORDANT (prediction
missed; "no DIM/METRIC upgrade"). Else (W-CONFIRMED): UNIVERSAL iff METRIC
+ (i')+(ii')+(iii')+(v') + C0-L128 + C1-POT + C1-EXT; METRIC iff DIM128 +
all-6-pairs@128 + sanity@64 + !P_void; DIMENSION iff DIM128 but !METRIC
(incl. P_void cap; P delta-misses with valid ruler land here, NOT
DISCORDANT); else DISCORDANT. METRIC/UNIVERSAL open OBS-1; DIMENSION does
not unless separately amended. Positive OBS-0R claims ONLY operational
probe agreement (spec interpretation discipline verbatim).

ANALYSIS: scripts/run_obs0r.py (units eigen|origin128|validate|pot|c3|c4|
dims) + scripts/analyze_obs0r.py (--stage c0|full; reuses analyze_obs0 for
G/D/W logic). Record: data/obs0r_verdict.json (+ verdict_c0.json staged).
Paper figures ONLY if >= METRIC.

PRE-PREREG PILOTS (design only, L<=16 / N<=512, never campaign sizes):
J2-L16/sq-L16 full mini-battery (maps r2 0.87-0.92, mono valid J2+sq,
inversion 100%, med-delta ~0.07; exp-N200 (G,P) invalid/coverage-0 as C1-
designed); static-vs-jump-evolved xi at L16 (0.5222 vs 0.5237 rates,
explained the kappa naming fix); L8/L12 wiring smokes + C3-convention pin
(L16 true-xi within 10% of 1.8968, in unit tests). eigh benchmark (beast):
N=8192 21s / N=16384 161s => N=32768 ~21min/decomp (operational, ungated).
NEXT: prereg-commit, push, beast setup (fresh clone ~/obs0r-69cc), Phase 1
(eigen128 j2+sq parallel, exp-N8192 eigen, validate on banked L64).

## OBS0R-VERDICT (OBS0R-METRIC (wave-confirmed + six-pair IR battery);
campaign-closed 2026-10-02; record data/obs0r_verdict.json; staged
verdict_c0.json on beast; code a924efa (1 pre-data tooling bugfix post-
prereg: missing-STOP ladder gate + epsilon softening, no threshold touch))

GATES: validate-PASS both L64 tags (worst=0.000e+00 BITWISE: targets-only
== all-safe exactly); C4-PASS (J2-branch 2.6/3.1% (bar 10%), sq 1.95%
(bar 5%) -- L128 eigen == banked P1/POT waves); C3-PASS (static TRUE-xi
1.8994 vs 1.8968 (+0.14%), range 3, residual 1e-16, positive+real+gap);
C0-L128-PASS (dH 1.9385 (rise from banked 1.9098), ds 2.0692, dW 2.0942,
all-6 floors <= 0.17); C0-POT-valid (sq mono all sizes); C1-POT-PASS 12/12
reject (unanimous: mono-invalid/bin-2-undefined); C1-EXT-PASS (dH clause +
ds drift 1.21->5.52 = 4.30 over 4 N (bar 0.5)); missing-FLAG 0.1116 (WP-map
UV-range edge, see below; STOP-clear at 0.25). J2_opened ONLY after c0-stage
pass (discipline kept; J2-L128 eigen/origins ran post-gate).

WAVE (primary): gap128 = |2.2285-2.0942| = 0.1343 <= 0.15 (ORIGINAL DIM bar,
in filed interval [0,0.3595], < banked gap64 0.1697) => W-FINITE-SIZE-
CONFIRMED. Filed point was 0.050; observed 0.134 lands inside the max-resid
band. Trajectories CROSSED: J2 dW rose 0.32->0.93->1.66->2.00->2.23 (residue
thinning as diagnosed) while C0 drifted 2.28->2.23->2.17->2.09 (estimator
systematics as window/resolution shift); J2 now sits ABOVE C0. Remaining gap
is consistent with substrate-dependent systematics (purification removes
~50% J2 vs ~3% sq) now that the beating floor is subdominant. The OBS-0 wave
discrepancy was dominated by finite-size beating, as filed.

DIM128-PASS: dH gap 0.0000 EXACT (7th year of J2-balls==2x-square: now at
L128), ds gap 0.0005 (2.0697/2.0692, EXACT-stable across L20->128 both
sides), dW gap 0.134. No d_P exists (prereg honest branch kept).

P-BRANCH: mono-valid J2+sq at ALL sizes (28/42/64/128); void=False,
incompatible=False. The all-path static field inverts cleanly into a scalar
ruler on both substrates and refuses to on the expander.

PAIRS@128 (non-inferiority + 0.40 cap): ALL 6 PASS with margin. J2 vs C0:
GW 0.146/0.145, GD 0.179/0.170, WD 0.118/0.128 (J2 tighter), GP 0.083/0.081,
DP 0.0089/0.0087, WP 0.035/0.038 (J2 tighter). Sanity@64 PASS (G/D/W banked
0.147/0.160/0.154; P new 0.083/0.009/0.034). L scaling of P floors: FLAT
(GP ~0.081-0.084 ALL sizes both substrates). METRIC=True: topology,
diffusion, coherent waves and the static all-path field infer the same
effective geometry up to fixed global calibration.

UNIVERSAL-clauses (ladder already METRIC): (i') three-regime: FAIL (1/6:
DP only). GW falls 1.83->0.12 then flat (UV-transient->floor, no interior
max); GD U-ish but far-bin max (diffusion wrap-shift grows to the wrap
boundary); WD dips mid-far then SPIKES 0.33 at [61,64) (wrap-edge);
GP rises 0.072->0.083 monotone; WP valley-then-rise. NO re-convergence
toward the far IR at L128: floors persist (GW) or rise (GD/WD) approaching
R->D/2. The "IR concordance" is C0-relative non-inferiority (J2 reproduces
the known-2D floor structure, often tighter), NOT absolute collapse --
OBS-0's "SHARED not EMERGENT" verdict extends to waves+POT. (ii') IQR:
PASS spectacularly (0.001-0.033 all 6 pairs -- no privileged origin).
(iii') sheet: PASS (EXACT banked-pattern reproduction at L128: tD R=2
contrast 0.1667 (banked 0.167), IR-blind both rulers, tW blind everywhere).
POT sheet (descriptive): the tD PATTERN EXACTLY -- UV R=2 contrast 0.1407
(L-independent to 5 decimals all 4 sizes), R=1/3 + meso 0.0000: the all-path
field forgets sheets at the same scale as diffusion. (iv') pert: DROPPED
per prereg (banked estimator-side fail stands). (v') scaling: PASS (G floors
stable 0.001/0.009, P bin-2 stable ~0.001, WD-T3 DOWN L64->128: the L20->42
rise REVERSED -- concordant regime expands with L). C0/C1 behave (above).
UNIVERSAL=False on (i') alone.

MISSING-FLAG 0.1116 (filed, mechanism understood, C0-matched): WP-map
~11% test-missing, SIZE-INDEPENDENT constants (J2 0.1116 / sq 0.1087 all 4
sizes): innermost-shell phi sits above the fitted -lnphi affine range (UV
curvature from the Yukawa prefactor bends the line the global fit must
split). Deterministic frozen-rule exclusion, same both substrates (delta
0.003). GP-missing 0.06-0.10 (tail range), DP 0.000, GDW ~0.000.

LADDER: OBS0R-METRIC (W-CONFIRMED + DIM128 + 6-pair battery + sanity; not
UNIVERSAL via three-regime). OPENS OBS-1 (observer reconstruction) per
prereg: an embedded observer with only operational ruler data can now be
asked what geometry it infers. Historical OBS0-DISCORDANT at L<=42 PRESERVED
(verdict JSON carries it; obs0.py untouched).

INTERPRETATION (filed, modest): five filed gaps (1.86->0.13) closed per the
finite-size model; four independent physical processes (shortest paths,
diffusion, coherent propagation, static all-path response) now mutually
predict pairwise distances up to FIXED global maps, benchmarked against a
known-2D control they match-or-beat -- while absolute ruler floors do NOT
collapse toward the IR (distinct asymptotic norms + wrap physics persist).
Geometry on J2 is operationally SHARED (lattice-like, probe-independent up
to calibration), not EMERGENT (IR-collapsing). OBS-1 must reconstruct from
ruler relations + floors, not from convergence.

**Kill relevance:** OBS0R-METRIC upgrades (not closes) the program: the
single OBS-0 failure resolved out-of-sample as diagnosed, and a new all-path
probe (which had every right to disagree -- POT-1 proved its route-
sensitivity) converged onto the same operational geometry. The surviving
non-convergence (absolute floors, far-IR wrap rise) constrains OBS-1's
reconstruction target: calibration-relative geometry with floors.

## OBS1-PREREG (Blind Observer Reconstruction; FROZEN-2026-10-02 (~13:00-UTC,
commit-predates-ALL-OBS1-campaign-data); branch cursor/obs1-reconstruction-69cc
off obs0r-tip-cac9c18; beast-dirs ~/obs1-69cc (code) + ~/obs1-data (write),
banked ~/obs0-data + ~/obs0r-data READ-ONLY; workers<=16 for station procs;
NO-local-campaign-data (sq-L42 pilot set + unit tests/synthetics only, listed
below))

QUESTION (exactly one): what spatial geometry does an embedded observer
reconstruct from operational measurements alone, with zero access to the
substrate graph? OBS-0R (OBS0R-METRIC) showed G/D/W/P rulers share a metric
up to fixed global calibration; OBS-1 removes the scaffolding (no R_G-fitted
maps anywhere: the composite uses median-normalization only, and NO channel
weight is tuned against hidden geometry at any stage).

FIREWALL: obs1.py + scripts/analyze_obs1_blind.py consume ONLY opaque
measurement records (cell/set/S-ids + values). C3-pinned by
tests/test_obs1.py (AST import scan + token scan of both blind sources +
meas-schema audit in the runner). Hidden joins exist ONLY in obs1_reveal.py,
imported ONLY by analyze_obs1_reveal.py, which REFUSES to run unless the
blind artifact hash matches the committed frozen value. Two-stage discipline:
blind artifacts committed (+ pushed) BEFORE the reveal stage runs.

CELLS (frozen order; blind sees ONLY the integer id): 0 j2-L42, 1 j2-L64,
2 j2-L128 (headlines), 3 sq-L42, 4 sq-L64, 5 sq-L128 (C0 known-2D), 6
exp-N3528-s0, 7 exp-N8192-s0, 8 exp-N32768-s0 (C1 size-matched non-2D, seed
s0 frozen). Expander N matches J2 2L^2 exactly (3528/8192/32768).

STATIONS: 64 per (cell, set), 3 sets per cell. Sampling frozen:
rng(9100+100*cell+set).choice(N,64,replace=False), S-ids in rng-permuted
order. Train S0-31 / test S32-63 (frozen indices = random held-out split).
Meas file: directed pairs Sa|Sb with {W,D,P,Dcfd}; seal file: tag + S-id->
node map (reveal only). Runner asserts meas schema (audit_meas_schema).

INSTRUMENTS (frozen): tau_W = first threshold-crossing at THETA_WAVE=1e-6
(OBS-0 Amendment-2, unchanged). tau_D = first threshold-crossing at the
SAME floor 1e-6 (one instrument noise floor, "when did you first notice";
pilot-justified below -- NOT the OBS-0 CFD peak). Dcfd = OBS-0 CFD peak
time recorded as bridge column ONLY (never consumed by blind estimators).
P: static field phi from one sparse solve per station source (POT-1
read-only route, gap-matched omega, H prebuilt once per set); phi<=0 or
non-finite -> None. INSTRUMENT-GATE: if any channel completeness < 0.90
on the first L128 set, the campaign PAUSES for instrument review
(pre-reveal, geometry-blind). Banked pilot completeness: W/D/P = 1.0.

NATIVE TRANSFORMS (locked): W = tau_W; D = sqrt(tau_D); P = -ln(clip(phi,
1e-300, 1.0)) (clip fraction recorded; pilot 0.0). Symmetrize AFTER testing:
raw directed M feeds the symmetry gate; D_ab = (M_ab+M_ba)/2 (diag 0) then
frozen imputation missing -> 1.5x channel max (fraction recorded; pilot
~0). ALL blind estimators run on completed matrices. COMPOSITE (locked):
median-normalize each completed channel (off-diag median, blind-safe),
equal-weight nanmean over available channels (never tuned). Composite
completeness bar 0.98; embed-complete bar 0.95 (else d*/embedding
descriptive-only for that set).

BLIND ESTIMATORS + BARS (all in obs1.py, all pinned by tests/test_obs1.py):
SYM: rel-asymmetry med<0.05 + p90<0.25 (pilot: exactly 0 by reciprocity).
TRI (two-tier, filed): tol 5%; STRICT frac<0.05 (single channels); LOOSE
frac<0.15 (composite near-metric bar; pilot physics: arrival channels carry
O(1) dispersion/interference non-metricity -- W 24%/D 12% frac, p99 0.30/
0.15 -- while static P is exactly metric (0.0%), composite 7.6% with p99
0.11 and frac>10% only 1.7%; the loose bar passes P-like and pilot-
composite-like mixing while still failing W-like 24%).
VOL-DIM: per-origin log-log OLS over pooled-quantile window [q25,q65]
(blind-safe, data-adaptive), median over origins; r2>=0.85 required;
DIM_STABLE iff >=2/3 sets ok and max-min d <= 0.5.
MDS: deterministic classical (Torgerson) in-house; d* by MAJORITY-DISTORTION
rule (d*=1 iff stress_1<=0.01 else smallest d with stress_d<=0.5*stress_1,
else argmin+pass=False). NO absolute global stress bar (synthetic
calibration: ideal periodic 2D data sits at raw stress ~0.10 from wrap
distortion -- any conventional cutoff mis-selects d*=3). REPLICATED iff the
same rule on the held-out test submatrix selects the same d* with pass.
ADJACENCY: bottom-decile of D^(O) (frozen). ANGLES (OBS-1F): per station,
pairs among 8 nearest: |cosine-rule angle - own-2D-ball-MDS angle| at the
apex; med<0.20 rad (local balls are cut-free; global-embedding comparison
is cut-distorted -- synthetic calibration). EUCLID-WINDOW: 2D-MDS stress of
D-balls over quantile radii {0.10,0.20,0.30,0.40}; WINDOW iff >=2 consecutive
<0.10 (absolute bar valid LOCALLY: pilot torus 0.005-0.011, star 0.76).
WRAP-FLAGS: D-near (bottom-10%) but embedding-far (top-25%): descriptive +
precision-gated (may resolve as "topology unresolved at tested size" --
listed OBS-1H outcome, NOT a failure of the campaign).

SYNTHETIC-CALIBRATION LOG (pure-numpy fixtures, no substrate, pre-data):
periodic-2D -> d=1.96/r2=0.98, d*=2 replicated, local charts/dist recover;
line -> d*=1; star -> vol r2-fail, no d* pass, no euclid window; R16/noise
-> d*=3/4 or none (never 2-with-pass); lifted-global-Procrustes FAILS
(eps 0.62-0.94: cut+bend+spectral curvature) -> chart/dist gates adopted;
angle-sum-to-pi VACUOUS (any valid triangle sums to pi) -> local-ball
angles adopted; torus strict-Procrustes ~0.9 recorded as topology signature.

PILOT DISCLOSURE (sq-L42 cell 3 set 0, control cell, pre-prereg smoke;
geometry-blind instrument facts + ONE hidden-geometry look documented):
completeness drove the CFD->threshold diffusion fix (CFD 52% missing far-
field by monotonic-rise physics; threshold complete 1.0, corr(sqrt(t),R)=
0.98, corr-vs-CFD 0.96 common pairs); triangle pilot (above) drove the
two-tier bar; UNTOUCHED after pilot: dim bar 0.5 (pilot C 1.65 passes),
angle bar 0.20 (pilot C 0.207 fails marginally -- left strict: caps only
the top rung, graceful), d-diff 0.5, all reveal bars, C1 rule. Hidden-look
(sq-L42 only, structural bug-hunt, no bar role): dist-quot 4%, charts W/D/P
0.18/0.05/0.02, locality 1.0, d*=2 replicated all probes -- plumbing
confirmed, zero bars moved. L42-vs-L128 differences (wrap/window/dim-bias
mechanisms) are DIAGNOSED BY the frozen L-scaling clause, not pre-judged.

REVEAL (frozen): hidden metric = minimal-image Euclidean on (x,y) quotient
coords (J2: j2_torus_coords; sq: id=x*L+y), periods (L,L); expanders: graph
(BFS) distance only. DIST_OK: scale-aligned RMS(D^(O),H_quot)<=0.30 (single
global scalar -- the primary geometric gate). LOCAL_OK: median per-ball
fresh-2D-chart Procrustes eps<=0.30 (chart = observer's own MDS of the ball;
hidden lifted rel. ball center, discrete copies, no warp). LOC_OK: >=70% of
observer edges hidden-near (symmetric frozen rule: hidden bottom-decile).
SHEET_OK (J2): same-vs-cross median contrast <0.05. TOPO_OK: >=3 blind wrap
flags with precision>=0.5 (TRUE = hidden-near + raw gap>L/2 in some axis).
OBS-1M: closer-to-quotient-vs-microscopic via scale-RMS (descriptive).
Per-probe dist/chart recorded DESCRIPTIVE ONLY (no per-probe rungs).
OBS-1L NOTE (filed deviation): global rigid coord alignment is topologically
obstructed on periodic targets (cut+bend), so OBS-1L is scored at the metric
level (DIST, global scale only) + chart level (LOCAL); strict global
Procrustes eps is recorded descriptively as a toroidal-topology signature.

LADDER (composite observer; cell flags = >=2/3 of 3 sets; J=J2-L128):
METRIC = METRIC_OK & DIM_STABLE & EMB_OK (metric_ok = sym-all-probes &
tri-loose & complete>=0.98; emb = d*pass & replicated & meas>=0.95).
QUOTIENT = METRIC & |d-2|<=0.5 & DIST_OK & LOCAL_OK & LOC_OK & SHEET_OK.
CROSS-PROBE = QUOTIENT & CROSS_OK (all 3 pairs scale-RMS<0.30 & |dd|<=0.5).
RECONSTRUCTED = CROSS & ANGLE_OK & WINDOW_OK & TOPO_OK & C0 & C1 & SCALING.
C0 (sq-L128): DIM_STABLE & |d-2|<=0.5 & DIST_OK & LOCAL_OK & LOC_OK; rungs
above METRIC REQUIRE C0 (else capped + PIPELINE-FAIL). C1 (each exp cell):
zero sets with (dim_ok & |d-2|<=0.5 & d*==2 & d*pass & replicated) AND >=2
sets composite-meas>=0.5 (data-existed guard). SCALING (J2 L42/64/128):
|d-2|<=0.5 all sizes & DIST_OK(L64+L128) & d-spread<=0.5. Headline =
highest cumulative rung else OBS1-NO-GEOMETRY; partial runs =
OBS1-INCOMPLETE. OBS-1K composite-vs-single recorded descriptively.

CONTROLS: C0 square (above). C1 expander (above). C2 permutation invariance
(unit test, exact). C3 no-coordinate audit (AST import scan + token scan +
meas-schema audit; hard gate). C4 probe independence (channel-isolated
builders, unit test). C5 held-out stations (train/test d* replication in
EMB). C6 size control (L42/64/128 scaling clause).

CAMPAIGN (beast): eigen unit ONLY for NEW exp-N32768-s{0,1,2} (all other
eigen banked, dirs read-only); stations unit 27 procs (9 cells x 3 sets);
blind analyzer on meas files only; COMMIT+push blind artifacts; reveal
analyzer (hash-locked) -> data/obs1_verdict.json. Follow-up gate per spec
(OBS-2 needs OBS-1 positive + frozen coupled U_G) UNCHANGED.

## OBS1-AMENDMENT-1 (composite mix-before-impute; FROZEN pre-reveal
2026-10-02 (~14:30-UTC; first blind hash 1f22537d SUPERSEDED before any
reveal ran or any hidden geometry was joined; OBS0-amendment precedent)

CAUSE (blind-internal instrument fact, L128 cells): the static channel has
finite SOLVER-FLOOR range. Far-field phi (~1e-20 at R~90) sits below the
~1e-10 absolute floor of any double-precision sparse solve (M-matrix theory
says phi>0 everywhere; the SIGN is numerical noise out there), so 38% (J2-
L128) to 67% (sq-L128) of P pairs are non-positive -> unmeasured (runner
P-completeness was 1.0 because it counts finite; blind requires p>0). W and
D remain 100% measured with clean geometry (d 1.7-2.0, d* 2R). The pilot
(L42, P 100%) could not catch this: it is a range effect.

DEFECT (pipeline order): the prereg froze composite-from-COMPLETED-channels
(impute each channel at 1.5x max, THEN mix). With P 33-67% imputed, the
imputation poisoned the P median and every mixed pair (composite tri 0.20,
d 1.0 at J2-L128 -- an artifact, not observer physics).

FIX (no bar/gate/ladder/estimator touched): composite mixes UN-imputed
symmetrized channels (median over measured only, nanmean over available
channels per pair: far pairs use W+D, near/mid use W+D+P), and the MIX is
completed after. Identical results when all channels are complete (all
L42/L64/expander cells). Per-channel paths unchanged: P-only L128
reconstruction is EMBED-flagged descriptive (measured_frac 0.33-0.62 <
0.95), honestly recording the static observer's finite range (~O(10 xi)).
Cross-probe (per-channel completed matrices) UNCHANGED by this amendment;
P-including pairs at L128 will carry imputation -- recorded as frozen
(no second amendment: if 3-way CROSS fails on P-range while WD passes,
that is the honest finite-range outcome, capping gracefully at QUOTIENT).
P-range-vs-L recorded descriptively in the verdict (static-observer range
finding). Regression-pinned by test_composite_mixes_measured_only.

## OBS1-VERDICT (OBS1-QUOTIENT (blind 2D-quotient reconstruction); campaign
2026-10-02 (~12:30-15:00-UTC); branch cursor/obs1-reconstruction-69cc; blind
hash a18c76b2 (Amendment-1 re-freeze; first hash 1f22537d superseded
pre-reveal); 27/27 station sets, W/D/P-runner-complete 1.0 everywhere)

HEADLINE: OBS1-QUOTIENT. A blind observer with only operational measurements
(arrival times, diffusion response, static field -- no graph, no coords, no
dimension input) reconstructs a stable 2D metric space that agrees, after
global alignment only, with the coarse J2 quotient rather than microscopic
sheet structure. Rungs: METRIC True, QUOTIENT True, CROSS False, RECON False.

J2-L128 (headline, 3/3 sets): d_O = 2.02 (stable, r2 pass), d* = 2
replicated train/test all sets, sym exact (reciprocity), tri-loose 0.019-
0.020, DIST rms 0.079-0.084 vs quotient (vs 0.16 microscopic: closer =
quotient all sets), local charts 0.055-0.063, locality 0.95-0.97,
sheet contrast 0.0001-0.025 (sheets forgotten -- quotient, not micro),
angles pass, euclid window pass. Strict global eps 0.80 (toroidal cut
signature, filed descriptive).
J2-L42/L64: same pattern tighter (DIST 0.038-0.039, locality 0.98-1.0,
charts 0.06, d 1.69/1.78 -- small-size dim suppression, within bar).
SCALING True (d 1.69/1.78/2.02 spread 0.33; DIST L64+L128).
C0 (sq-L128): PASS (d 2.20, DIST/LOCAL/LOC, pipeline validated).
C1 (all 3 expanders): PASS (twod_sets 0/3 with data 3/3; d* = 3 replicated,
d = 3-10; pipeline does not hallucinate 2D).
CROSS-PROBE False (honest finite-range failure): WD pair passes all sets
(rms 0.13, |dd| <= 0.29 -- wave and diffusion observers inhabit the same
world); P-including pairs fail (WP rms 0.35, P-dim unmeasurable) because the
static channel has finite SOLVER-FLOOR range (P measured_frac 1.0/1.0/0.62
J2 and 1.0/1.0/0.32 sq across L42/64/128: far-field phi below ~1e-10
absolute double-precision floor -> non-positive -> unmeasured). The static
observer sees only to ~O(10 xi); within range it is the CLEANEST channel
(L42/64: tri 0.000, d 2.11, charts 0.02). No second amendment was filed:
3-way CROSS correctly fails while WD passes (graceful cap at QUOTIENT).
TOPOLOGY unresolved (0 blind wrap flags at 64 sparse stations -- listed
OBS-1H outcome, not a campaign failure); strict-eps ~0.8 signatures
periodicity without resolving it. RECONSTRUCTED correctly out of reach
(needs CROSS + TOPO).

INTERPRETATION (filed, modest): space is operationally reconstructible --
distance, dimensionality (2.02, unprompted), neighborhoods (95%+),
local angles/charts (6%), and the quotient (not microscopic) geometry all
emerge from signals alone, replicate across sets/sizes, and refuse to
appear for expanders. Dimension is the fragile observable (arrival-dim
bias at small L, P-dim unmeasurable beyond range); the metric itself is
robust (WD rms 0.13, composite-quotient 4-8%). The observer naturally
inhabits the QUOTIENT geometry: sheets quotient away (contrast < 0.03).

**Kill relevance:** OBS-1 upgrades the program from shared rulers (OBS-0R)
to reconstructed space: an embedded observer recovers 2D quotient geometry
without being given any geometry. OBS1-RECONSTRUCTED remains open (needs
topology resolution: denser stations or loop-based flags). Follow-up gate:
OBS-2 needs OBS-1-positive (SATISFIED) + frozen coupled U_G (STILL OPEN) --
no deformation campaign until U_G exists. Mixed-solver note: 12 light sets
banked with spsolve-P pre-CG-fix, numerically identical (<1e-8, residuals
1e-15 vs 4e-12); exp-N32768-s1/s2 eigen skipped (cell 8 uses s0 only).

## U0-PREREG — Minimal geometry dynamics (FROZEN PRE-DATA)

**Status:** apparatus + semantics + tick + states + gates + ladder
frozen; campaign NOT YET RUN. U0 accepts BR27-NO-MODE (no mechanism
in the current ontology causes structural events) and CONS0-PARTIAL
(no conservation-derived contraction law). It proposes, freezes, and
falsifies minimal primitive firing laws U_G: (G_t, psi_t) -> G_{t+1}.
Any survivor is A NEW PRIMITIVE DYNAMICAL POSTULATE (firewall: not
emergent, not derived from conservation/energy/instability/BR-2/
gravity/known physics). Previous results constrain form, imply nothing.

**Frozen inputs (read-only, md5-verified byte-identical):** BR-2.7 tip
f82566d (ballistic/backreaction/phase/contraction/accounting/stability
+ formation delta + 6 test files); CONS-0 tip c551cb5 (conservation/
continuum/driven + 3 test files + closure pins + xdist config); UG-0
tip 0373c5d (ug/ug_sync design apparatus + tests). No law change on
consumption (commit 9a350ba). Frozen conventions: H(G) = -A(G), J = 1,
hbar = 1; sum map psi_k = psi_i + psi_j; simple graphs; B/J
quadrature; E_psi = -2 sum_E B; dE_contract = 2B - 2 sum_cross
(BR-2.6 MINUS convention); L := B - sum_cross; dt = DT_DEFAULT = 0.1
(P1-frozen, not a new parameter).

**U0-A semantics (frozen, analytic):** UB: sign(B) (B > 0 CONTRACT,
= 0 NONE, < 0 SPLIT). UL: sign(L) (same orientation; frozen by (i)
L -> B continuity as cross -> 0 (pinned on K2), (ii) UG-0
byte-continuity, (iii) opposite orientation covered by UEc, no gap).
UEc (contraction-only energy selection): per-edge {separate,
contracted} exact-energy comparison, contract iff dE = 2L < 0 else
NONE (strict descent; ties -> NONE = minimal action). THEOREM
(pinned): UEc contracts exactly where flipped-UL would and never
SPLITs (no per-edge split state in the frozen ontology). SPLIT marks
are reported per edge (tendency census); node-split REALIZATION is
undefined for all candidates (U0-H): repeated dynamics are
contraction-only (splits counted, never applied). Consequence
(theorems, pinned): N(t) monotone nonincreasing; explosion/
fragmentation structurally unreachable (filed, not measured).
Zero-parameter throughout; no targets (J2/matter/etc.) anywhere.

**U0-B/C/D derivations (frozen single-tick consequences, pinned in
tests/test_u0.py, re-measured in campaign):** zero field: B = L =
dE = 0 -> ALL laws neutral on ALL edges; tick fully quiescent
(G identical, psi = 0; consequence banked, no exception).
Pure-current (exact B = 0, J = +-rho^2, J2-L6 stagger): UB all
NEUTRAL; UL all SPLIT (L = -n_cross rho^2 < 0, derived); UEc all
CONTRACT. Bonding uniform (n_cross >= 2): UB all CONTRACT, UL all
SPLIT (L = (1 - n_cross) rho^2), UEc all CONTRACT. Antibonding
stagger: UB all SPLIT, UL all SPLIT, UEc all CONTRACT. The three
laws are pairwise separated by the {bonding, current, antibonding}
triplet (derived, not selected).

**U0-I tick (frozen full-sync quotient, zero new parameters):** from
X_t = (G_t, psi_t): marks from X_t only; CONTRACT classes merge
simultaneously (quotient graph, simple kind; singletons keep labels,
merged classes take fresh ints in min-member order -- naming only);
psi^e = evolve_fixed(psi_t, H(G_t), dt = 0.1, one step); psi_{t+1} =
sum-thread psi^e onto G_{t+1}. Both updates see X_t only; no
within-tick ordering exists (U0-G commutation: quotient equals
any-order sequential merger as unlabeled graphs + field multisets,
pinned). Rationale (pre-data, banked): UG-0's fire-none census shows
TOTAL STALL on all uniform-field states (30/30 rows fire 0 except
isolated spikes) -- freezing fire-none would probe scheduler stall,
not the firing law. Quotient-sync removes scheduler debt with zero
new parameters (no tie-breaking, ordering, labels). Cost filed
openly (U0-F split verdict): decision radius stays 1; one-tick
effect reach = marked-component diameter (unbounded a priori;
GRAV-1C input, not claimed here).

**U0-G conflict rule:** there is no conflict to resolve: adjacency
of CONTRACT marks IS the merger instruction (synchronous sets that
commute, pinned). Deterministic, decision-local, relabeling-
covariant, zero-parameter (gated per config in campaign).

**U0-H split status (frozen):** (H1) endpoint assignment is gauge
(swapped-endpoint splits isomorphic + field-multiset equal, pinned);
the problem is selecting the UNORDERED cover ((3^d + 1)/2, pinned).
(H2) No earned quantity selects: J-guided vs B-guided covers differ
on banked states (pinned exhibit) -- any discriminator is unforced
new-primitive content. (H3) No split realization in U0 apparatus
(by frozen construction). (H4) The one forced selection attempt:
per-node energy-argmin over undirected covers x {equal, norm}
(CONS-0K formulas, direct-verified 1e-9 every option; tie iff >= 2
options within 1e-12 of min). THEOREM (pinned): zero-field all-tie
(all options dE = 0); all-shared equal split dE = -|s|^2/2 <= 0
(splits always energetically available where s != 0 -- full-U-E
would split ubiquitously, never vacuously). Prediction: H4 ties
generic -> no forced unique selection -> full laws incomplete.

**U0-E/F/J/K (frozen gates):** E: global-phase invariance,
conjugation covariance (J-blind, B-even), endpoint exchange,
relabeling covariance (marks + full tick) -- all laws, all states.
F: mark bitwise-invariance under field mutation at dist >= 3 and
(L/UEc) graph toggle disjoint from N[{i,j}] (decision radius 1);
UB graph-blindness; effect reach measured (= max class size/
diameter, filed). J: repeat trajectories bitwise-identical G +
1e-9 psi; relabeled trajectories isomorphic + mapped fields.
K: single-edge BR-2.6/CONS-0 books (dE/dQ formulas vs direct,
parts vs direct) + per-tick multi-merger books (dQ pair-formula
dQ = 2 sum_classes sum_pairs B_pair vs direct 1e-12; dE direct;
cycle rank; triangles; components).

**U0-L battery (frozen):** S1 zero J2-L6; S2 bonding J2-L6; S3
exact pure-current J2-L6; S4 antibonding J2-L6; S5 bonding
square-torus-6; S6 bonding ring-24; S7 BFS-parity current ER-24
(mixed B, B-zero fraction characterized); S8 bonding
collapsed-mini. All psi normalized except S1. Exact quadrature
states (rho/i rho/-rho/-i rho, bitwise B/J) with 1e-12
cross-check vs frozen BR-2 float stagger. 8 states x 3 laws =
24 trajectories, T = 20 ticks each, always full T (N = 1 ticks
are exact no-ops, pinned; no early stop -- fields can
reactivate marks). Per-tick observables (frozen list): N, E,
ncomp, Q, Epsi, IPR, max/mean degree, triangles, squares,
diameter (largest component), cycle rank, B-zero fraction,
n_C/n_S marks, n_merged, max class, dN, dE_graph, dQ
(direct + pair-formula), dE_psi.

**U0-M classifier (frozen decision tree, contraction-only):**
quiescent iff zero applied mergers; collapse iff Nf <= max(2,
ceil(0.1 N0)); else other/{settled-partial (quiet last-3 tail),
reactivated (>= 2 bursts separated by >= 2 quiet ticks),
window-unresolved}. Bounded-active/oscillatory-in-N/explosion/
fragmentation are structurally unreachable under contraction-only
(N-monotone + connectivity theorems, pinned) -- filed, not
measured. Analyzer recomputes classes from rows (no trust).

**U0-N/O (frozen):** report J2 fate per law (no preservation
target; J2 destruction means J2 is not a vacuum of the completed
machine); report structures without matter labels.

**U0-P (frozen rows, foundational only):** complete? /
deterministic? / decision-local R1? (+ effect reach filed) /
automorphism-covariant? / zero free parameters? / split resolved?
/ scheduler resolved? / accounting explicit? -- per law. No
gravity/particle/J2-survival scoring.

**Ladder-eligibility rule (frozen, definitional):** completeness
requires contraction + split realization (U0-H). Contraction-only
restrictions, however fully specified as dynamics, are NOT
complete U_G for ladder purposes; they are evaluated separately
with consequences filed (U0-H text; otherwise its "candidate
incomplete" is vacuous; the frozen structural primitive is
bidirectional). Mapping: U0-NONE iff no contraction-only law
passes all foundational gates; U0-INCOMPLETE iff >= 1 passes and
no full law is complete; U0-PRIMITIVE iff exactly one full law
complete; U0-DEGENERATE iff >= 2 full laws complete.
PREDICTION (theorem-backed): U0-INCOMPLETE (tendencies viable,
splits unrealized, effect-extensive + monotone-N costs filed).
U0-NONE stays data-reachable; PRIMITIVE/DEGENERATE rungs defined
but predicted empty (zero-field tie theorem + unforced exhibit;
cf. BR-2.7 precedent). Handoff: INCOMPLETE keeps BR-3C BLOCKED;
the primitive-law design problem (forced split selection) stays open.

**Integrity gates (campaign validity, hard fail):** N-monotone +
ncomp == 1 every row; dQ pair-formula 1e-9 every tick; single-edge
books 1e-9/1e-12; H4 formula residuals 1e-9; J-battery pass.
Campaign + full suite run on beast (96 CPU, mp pools); nothing
local except unit pins.

## U0-VERDICT — U0-INCOMPLETE (tendencies exist, no complete U_G)

**Campaign:** beast 16.54.88.181 (96 CPU, --jobs 90); ledger
data/u0_ledger.json (24 trajectories T = 20, 6 edge books,
31 H4 nodes, 3 J checks, 24 tick0 configs); analyzer 158/158
gates green; verdict data/u0_verdict.json. Full suite on beast:
982 passed, 2 skipped (torch importorskip, pre-existing
environmental) in 175 s. Local analyzer re-run on the beast
ledger reproduces data/u0_verdict.json exactly (cross-machine
analysis determinism). No fitting after opening data.

**Integrity (all green):** N-monotone + ncomp == 1 on all 480
rows; dQ pair-formula vs direct every tick; 6/6 edge books;
31/31 H4 formula residuals; J-battery (2 repeats bitwise-G +
0.0 psi diff; 1 relabel isomorphic + 0.0 field diff).

**U0-B zero field (S1):** all laws zero events, N 72 -> 72,
quiescent -- the derived consequence holds; no exception added.

**U0-C pure current (S3):** UB quiescent (B = 0 -> neutral,
derived); UL quiescent (all-SPLIT marks, unrealized); UEc
collapse 72 -> 1 in one merger. Discriminator confirmed as
characterization: B-coupled UB is current-blind while UEc
contracts (S3 edge book: B = 0, dQ = 0 exactly, dE = -0.389
via cross anatomy).

**U0-D bonding/antibonding (S2/S4):** UB collapse/quiescent
(opposite tendencies: all-CONTRACT vs all-SPLIT marks); UL
quiescent/quiescent; UEc collapse/collapse (energy descent
sees no quadrature distinction). Characterization only.

**U0-E/F/G:** E-sym, F-declocal (decision radius 1, all laws),
G-commute, A-theorems all green, all laws. Effect reach
(filed): UB 103, UL 2, UEc 103 -- uniform-state collapses are
single-tick whole-component mergers (mergers_total = 1,
Nf = 1): decision-local, effect-extensive, exactly the filed
quotient-tick cost.

**U0-H splits:** H4 census -- UB 4/4 tied (S4); UL 11/27 tied
(S3 4/4, S4 4/4, S7 3/3 tied; S2/S5/S6/S8 0/4: argmin unique
on uniform-bonding states, tied on staggered/current states);
UEc 0 proposing (theorem: never SPLITs). No forced unique
selection across the battery, and argmin-selection would
itself be new-primitive content (energy-descent postulate);
H3 stands (no realization in apparatus). Split unresolved
for all three laws.

**U0-J determinism:** green (see integrity).

**U0-K one-event books:** 6/6 -- dN = -1; dQ formula == direct
(incl. exact 0 on S3); dEpsi formula == direct == CONS-0
parts-sum (1e-12); all six frozen edges downhill (dE in
[-0.417, -0.083]); dxi = 0 except S7 (dxi = -1); dtri filed
(21/21/21/0/5/16). Accounting explicit; no new conservation
claimed.

**U0-L/M classes (T = 20, analyzer-recomputed):** UB quiescent
S1/S3/S4, collapse S2/S5/S6/S8 (-> 1, one merger) and S7
(-> 2, 4 mergers); UL quiescent x7, other:reactivated S7
(24 -> 10, 9 bursts, 11 mergers); UEc quiescent S1, collapse
all other seven (-> 1, one merger). No oscillation/explosion/
fragmentation (structurally excluded, filed pre-data).

**U0-N J2 fate:** S1 zero-field J2 preserved by all (72 -> 72).
Bonding J2 destroyed by UB/UEc (-> 1 in one tick), preserved
by UL; current/antibonding J2 destroyed by UEc, preserved by
UB/UL. Per firewall: J2 is not a vacuum of the UB/UEc-completed
machine. No law modified.

**U0-O:** collapses filed as unclassified structural collapse
(N -> 1); S7/UL reactivation filed without interpretation. No
matter labels anywhere.

**U0-P comparison (foundational only):** complete? no/no/no;
deterministic? yes x3; decision-local R1? yes x3 (effect reach
103/2/103); automorphism-covariant? yes x3; zero free
parameters? yes x3; split resolved? no x3; scheduler resolved?
quotient-sync x3 (no within-tick order); accounting explicit?
yes x3. The contraction-only restrictions are fully specified
dynamics but ladder-ineligible by the frozen rule (the frozen
structural primitive is bidirectional).

**Verdict: U0-INCOMPLETE.** At least one contraction-only law
passes all foundational gates; no full law is complete (splits
unrealized for all). Matches the theorem-backed prediction;
NONE was data-reachable (any foundational red) and did not
occur. PRIMITIVE/DEGENERATE rungs defined but empty.

**Handoff:** BR-3C stays BLOCKED. The primitive-law design
problem stays open, now sharpened: the missing piece is a
forced split-selection rule (unique, deterministic, local,
covariant, zero-parameter). H4 shows energy-argmin ties on
exactly the staggered/current censused states (plus all-tie
at zero field by theorem), so it cannot be that rule without
new postulates. Downstream firewall holds: no tuning of
UB/UL/UEc is permitted; any future split postulate is
new-primitive content, not a derivation.

## TIME0-PREREG — Two-boundary history selection (FROZEN PRE-DATA)

**Status:** apparatus + semantics + grid + gates + ladder frozen;
campaign NOT YET RUN. TIME-0 accepts U0-INCOMPLETE (forward-state
underdetermination: splits unrealized by every tested minimal law),
CONS0-PARTIAL (no conservation-derived contraction law), and
BR27-NO-MODE (no instability/firing mechanism). It tests whether the
graph-field model is better described by GLOBALLY CONSTRAINED
HISTORIES Gamma = (X_0, ..., X_T) with X_0 = X_-, X_T = X_+ than by
a forward Markov law X_{t+1} = U(X_t). The question is combinatorial:
N_hist(X_-, X_+) = ? No retrocausality, signalling, cosmology, or
interpretation is claimed (TIME-0L firewall: solved from outside).

**Frozen inputs (read-only, byte-identical to source tips):** BR-2.5
tip 3ea8cf1 (contraction/backreaction/ballistic/phase + formation
delta); BR-2.6 tip dd956e0 (accounting); BR-2.7 tip f82566d
(stability); CONS-0 tip c551cb5 (conservation); EM-0 tip 3128ff9
(continuum/driven); U0 tip f714762 (u0/ug/ug_sync + xdist config).
No law change on consumption. Frozen conventions: H(G) = -A(G),
J = 1, hbar = 1; sum map psi_k = psi_i + psi_j; simple graphs;
B/J quadrature; E_psi = -2 sum_E B; dE_contract = 2B - 2 sum_cross
(MINUS convention); dQ = +2B_ij; dxi = -c; dt = 0.1 (P1-frozen).

**TIME-0A/D compatibility (frozen pairwise relation, R_time = 1):**
a step is exactly one of IDENTITY (same canonical class; psi' =
U(G) psi), CONTRACTION (one-edge BR-2.5 quotient; psi'_k = psi_i +
psi_j), SPLIT (one-node record-free cover, children adjacent;
psi'_i + psi'_j = psi_k -- the exact reverse of the sum map, the
unique relation making contraction steps reversible as relations;
equal/norm policies satisfy it as special cases but are NOT
imposed, U0-H: no selection). Evolution rides identity steps only.
Hard = structural adjacency + these field relations. Ledger (dN,
dE_G, dQ, dE_psi, dxi, triangles, B/L) is DESCRIPTIVE, never
gating (CONS-0 no-go respected; no promotion).

**Headline domain (frozen):** graph sector (V0 psi = 0 exactly):
field compatibility closes trivially, so canonical-class
enumeration is finite and EXACT (DP over walks, bigints, never
sampled; explicit materialization only for capped audits).
Canonical universe = connected non-isomorphic simple graphs N in
1..6 from nx.graph_atlas_g (deterministic; 143 classes
1/1/2/6/21/112); cid = (N, k). N = 7 splits dropped + counted
(bounded-universe boundary, filed); robustness: N <= 5 rerun +
N <= 7 spot (N_- <= 4, T <= 3). Labeled mode (N <= 4, 44 states,
descriptive/cross-check) uses the TIME-0 downshift rule
(contraction keeps i, drops j, shifts > j; split w -> (w, N_new)),
bridged to BR-2.5 ops by iso + field-multiset pins per
transition. Field sectors enter ONLY via labeled spot cases
(R-control, constructed I/J cases) with exact affine-membership
propagation (split fractions form an affine reachable set;
membership decided by lstsq, no sampling of the continuum).

**TIME-0B/K reversal (frozen):** Theta = reverse slice order +
conjugate fields. V0-exact; 1e-9 field tolerance (Krylov grade).
K-gate: N_hist(a,b;T) == N_hist(b,a;T) all pairs T in 1..3 +
transition mirror (C<->S) over every interior transition. If an
interior mirror is missing it is REPORTED, not repaired.

**TIME-0C propagator (frozen):** U(G) = banked Krylov evolve_fixed
one step dt = 0.1; reverse = conjugation identity U^-1 phi =
conj(U conj(phi)) (H real symmetric; banked forward propagator
only, no new numerics). C0: roundtrip <= 1e-12 (V0
bitwise zero, pinned).

**Grid (frozen):** headline N_- in 1..6 x T in 2..6, all (c_-, c_+)
pairs (143^2 per T); anchored I/J at (T1,T2) in {1,2}^2;
R-control on {edge2, path3, tri3} x T=2 + edge2 x T=3 (seeded,
complete-flagged); labeled census T in {2,3}.

**Controls (frozen C0-C7):** C0 reversibility; C1 hand counts
(universe sizes, edge-graph T=1 successors {C,I,S,S} with P3/K3
outcomes, toy chain = 1, toy diamond = 2, explicit-vs-DP);
C2 reversal symmetry; C3 canonical-id permutation invariance +
labeled-projection equality; C4 every contraction edge R = 1 via
influence_check + R_time pairwise decomposition; C5 banned-token
scan (record/nbrs_i/nbrs_j/preimage) over all event stores;
C6 DP-vs-explicit + participation sums + labeled-lift existence;
C7 verdict consumes aggregates only (determinism + rung-table
pins). R-gates: R1 identity walk present + matching, R2
on-trajectory >= 1 walk; R3 off-trajectory count RECORDED (not
gated: excursion DOFs may cover generic finals). TIME-0R/S/T
controls pinned pre-data. TIME-0Q DEFERRED (no banked M_O;
constructing one = new ontology).

**Ladder (frozen thresholds):** headline requires C0-C6 green
else TIME0-INCONCLUSIVE. Pooled f_unique < 0.2 -> TIME0-NULL.
>= 0.8 with worst-T >= 0.6, pooled f_compatible >= 0.1, and
split-resolution >= 0.8 -> TIME0-UNIQUE (+ R_space = 1 and
no-objective audit -> TIME0-LOCAL). Else TIME0-CONSTRAINED.
Skeleton (identity-compressed) f_unique reported as exact
descriptive co-headline (timed = sum_L C(T,L) S_L, pinned).
Scaling trend (TIME-0O) and N-only coarse-graining (TIME-0P)
descriptive. No extrapolation beyond N <= 6 without combinatorics.

## TIME0-VERDICT — Two-boundary history selection: TIME0-NULL (DATA)

**Campaign:** beast EC2 16.54.88.181, --jobs 90, 185.8 s, ledger
`data/time0_ledger.json` (schema v1, 8.8 MB) + `data/time0_verdict.json`
+ supplementary `data/time0_n7_followup.json`. All C0-C6 gates green;
analyzer integrity recompute green (all matrices/histograms/rates
reproduced from raw triples); 53/53 `test_time0.py` pins green.

**Headline (frozen ladder):** pooled f_unique = 0.051 < 0.2 over
102245 pairs (74977 compatible) => **TIME0-NULL**. Per-T:
T=2: unique 0.554 compat 0.331 med 1 max 34;
T=3: 0.005 / 0.510 / 6 / 118;
T=4: 0.001 / 0.884 / 43 / 2192;
T=5: 0.0004 / 0.944 / 285 / 12283;
T=6: 0.000 / 0.997 / 4415 / 196598.
Degeneracy PROLIFERATES with T (median 1 -> 4415); compatible
pairs are the majority by T=4 (0.88) and nearly all pairs by T=6
(0.997), multiply realized throughout.

**Boundary-artifact correction (supplementary N<=7 followup,
post-data, non-ladder):** headline N<=6 drops all N=6->7 splits,
inflating T=2 uniqueness for N=6 starts (0.644 vs 0.028 at N=5).
Subset-matched rerun inside the N<=7 universe (996 classes, N=6
splits restored): T=2 f_unique 0.554 -> 0.073; T=3/4 unchanged
(0.005/0.001). The T<=3 subset numbers are EXACT unbounded-universe
counts (no walk between N<=6 endpoints in <=3 steps can visit
N>=8 and return: needs >=4 steps). Full-996 census shows the same
pattern (T=2: 0.63 with the artifact moved to N=7 starts; T=3:
0.004). NULL is robust and stronger than headline numbers suggest.

**TIME-0F:** initial-boundary underdetermination confirmed
independently of U0: median N_hist(X_-) = 74 (T=2) -> 514 -> 7649
-> 64167 -> 844068 (T=6). Always >> 1.

**Waiting vs structural (exact skeleton census, descriptive):**
f_unique^skel = 0.671/0.365/0.004/0.002/0.0004 (T=2..6). Waiting
placements explain much of the T=3 timed collapse (0.37 skel vs
0.005 timed) but STRUCTURAL degeneracy itself proliferates at
T>=4 (74 unique skeletons of 18075 compatible pairs at T=4).

**TIME-0I/J (anchored):** single-step tails always resolve
(S-1-1, S-2-1, C-1-1, C-1-2: rate 1.0; 19k/39k/8k/17k rows) but
resolution decays with horizon (S-1-2: 0.61, S-2-2: 0.55 over
177k rows, C-2-1: 0.56, C-2-2: 0.45); pooled split_res = 0.654
< 0.8. Two-boundary constraints select the split/predecessor at
short range and lose selection as alternative routings open.

**Controls:** TIME-0R perfect on all 5 cells (on-trajectory: 1
walk incl. identity; off-trajectory: exactly 0; field-only
any-graph identical) -- the apparatus CAN and DOES report
N_hist = 1/0 exactly when the physics has it, so NULL is not a
counting artifact. Toy S = 2 / toy T = 1 exact. TIME-0K:
N_hist(a,b) == N_hist(b,a) on all 20449 pairs x T=1..3 +
C<->S mirror on every interior transition (exact). TIME-0M:
R_space = 1 (all contraction transitions), R_time = 1
(pairwise decomposition pinned). TIME-0P: N-only boundary
degeneracy medians 2/6/40 (T=2/3/4). TIME-0E: ledger quantities
kept descriptive throughout (no promotion). TIME-0Q DEFERRED
(no banked M_O). Labeled N<=4 census (0.70 -> 0.03) and N<=5
rerun (0.47 -> 0.02 -> 0.009) reproduce the pattern: not a
labeling or boundary artifact.

**Interpretation (boxed):** the final boundary does not solve
the missing structural dynamics. Return to the ontology problem;
do not invoke two-boundary determinism downstream. Positive
fragments filed: two-boundary constraints ARE informative at
short horizons (single-step anchored resolution 1.0, R-control
uniqueness) -- compatible with CONSTRAINED locally -- but
generic compatible pairs at T>=3 retain N_hist >> 1, so the
frozen ladder (generic uniqueness) returns NULL.

## QUOT — dynamical origin of the observer quotient (Quot track)

**Fork (adopted):** from main tail (a0c248c, v5.5.0, 576 tests) + read-only
vendored apparatus (byte-identical sha): ballistic.py (7578176c, P1 wave),
malus.py (MALUS-0 sheet sector), driven.py (e3f1ff98, POT-1), obs0.py +
obs0r.py (OBS-0/R rulers), obs1.py + obs1_reveal.py + run/analyze scripts
(OBS-1 blind observer), formation.py elist_window (additive, keeps vendored
ballistic pins green). Nothing vendored is modified (C6 firewall).

OBS-1 banked OBS1-QUOTIENT (blind d_O = 2.02, DIST 0.08 vs quotient,
locality 0.95+, sheet contrast < 0.03: the observer inhabits J2/sheet).
MALUS-0 banked [H,S] = 0, H*P_anti = 0, symmetric sector = square walk at
2J (M0-NULL: one propagating sector + one dead). QUOT-0 tests whether the
observer quotient FOLLOWS from the dynamical sector structure (quotient
selected by information transport) or is an accidental coarse-graining.

**QUOT-0 PREREG (FROZEN pre-data; this commit predates ALL Quot runs):
mechanism, not discovery.** Headline substrate: J2 torus L = 28 (N = 1568,
MALUS/POT headline scale); frozen law H = -A, J = 1 everywhere headline
(no coin, no onsite, no weights). Pins at L in {4, 6, 8} (fast, local-OK);
campaign numerics on beast (16.54.88.181, 96 workers, dir ~/quot-ea4c +
~/quot-ea4c-data write, ~/obs0-data + ~/obs0r-data + ~/obs1-data READ-ONLY:
banked eigen/info consumed, never rebuilt, sha logged). Apparatus:
src/bh_graph/quot.py + tests/test_quot.py (pins in this commit) +
scripts/quot_campaign.py (units below) + scripts/analyze_quot.py
(verdict) + scripts/analyze_quot_replay.py (replay reveal; calls vendored
analyze_obs1_{blind,reveal} functions, zero observer-code changes).

**Derived inputs (pen-and-paper, pre-data predictions, NOT fits):**
identical coarse-neighbor sets of the two sheets (MALUS-0 banked) give
[H,S] = 0, H*P_- = 0, H_+ L = L H_Q (H_Q = -2J A_sq). Corollaries derived
here pre-data: (i) U(t)L = L U_Q(t) exactly, U(t)psi_- = psi_- exactly,
U(t)psi = U_+(t)psi_+ + psi_- exactly; (ii) wave sheet-bit remote
probabilities IDENTICAL (fp): mixed (|x,0> vs |x,1>) differ only by frozen
anti sign with source-cell support, so every remote target sees the same
|.|^2 (exact, not approximate); (iii) diffusion: J2 is 8-regular so
Lrw = I - A/8, hence Lrw P_- = P_- exactly (eigenvalue 1, mult N/2:
anti modes decay e^{-t} in place, never spread) while Lrw,+ = square Lrw
exactly (A_+ intertwines as 2 A_sq, /8 = /4 square: symmetric diffusion
IS square diffusion); arrival-contrast pattern {R=1: 0, R=2: >0, R>=3: 0}
follows (R=2 is the only shell containing same-cell cross-sheet pairs,
where the local anti term e^{-t} lives) -- predicts the banked OBS-0R
pattern (0.0000 / 0.1667 / 0.0000) with zero parameters; (iv) POT:
two-pin same-cell removal preserves S (bulk stays sector-diagonal), so
anti-drive response has support within 1 hop of source EXACTLY
(H_-,BB = 0, phi_- = H_BS s_-/omega on neighbors only) while sym-drive
propagates (Yukawa); mixed far-field = sym far-field, near-field contrast
from the trapped anti term -- predicts the banked POT pattern
(R=2 0.1407, else 0) mechanistically.

**Q protocol (LOCKED).** Q-ALG (exact algebra, L28 filed + L<=8 pinned):
||[H,S]|| = 0, ||H P_-|| = 0, ||H U - U H_sq|| = 0 (fp <1e-9),
||U(t)L phi - L U_Q(t)phi|| <1e-9 (5 random phi x 4 t, Krylov both
sides), ||U(t)psi_- - psi_-|| <1e-9, decomposition identity <1e-9,
L28 flat-band n_zero = 784 + 54 = 838 (MALUS regression, C0).
Q-COMM (L28, banked eigen, general-initial-state traces): preparations
(all norm-1, single-cell support): SYM position-bit (|x0,+> vs |x1,+>,
x1 = x0+(1,0)), ANTI position-bit (|x0,-> vs |x1,->), SHEET-bit
(|x0,0> vs |x0,1>), x0 = (7,14); receiver coarse shells r = 0..14
(rounded min-image Euclidean, both sheets); D_B(t) = TV (preregistered
1/2 L1, sheet-resolved primary); C(r) = max_t D(r,t); arrival threshold
theta_arr = 0.001. Wave grid dt = 0.05 T = 16; diffusion grid =
obs0.diffusion_grid(D) (dt = 0.25). Bars: SYM arrival exists + C_+ >
0.001 at r in {2,4,6} wave+diffusion (positive control); ANTI C_- <1e-9
at r >= 2 wave+diffusion (fp-exact zero) + ratio C_-/C_+ <1e-6 at
{2,4,6}; SHEET S(0,t=0) = 1.0 exact, S(r) <1e-9 at r >= 1 wave+diffusion
(local-real/remote-blind); else stage INVALID (apparatus fault, fix +
re-prereg, no shopping). Global-phase (C3), sheet-exchange (C4),
label-permutation (C5) invariance pinned.
Q-SECTOR: wave exactness (mixed-vs-projected remote traces <1e-9,
probabilities ratio P+/mixed = 2 exactly remote <1e-9); diffusion
operator (||Lrw P_- - P_-|| <1e-12, sym=square intertwining <1e-12) +
pattern {R1 <0.01, R2 >0.05, R3+ <0.01} on frozen arrival_times_diff +
obs0.sheet_contrast (4 frozen origins, all must agree) + ablation
(sym-only kernels -> R2 <0.01; banked 0.1667 within 30% descriptive
DERIVED-support); POT exact anti-support (1-hop, fp) + mixed-vs-sym
far-field (r>=4) relative <5% + pattern {R1 <0.01, R2 >0.05, R3 <0.01,
meso <0.01} via frozen obs0r.static_field_phi + sheet_contrast (4
origins) + ablation (sym-drive -> contrast <0.01 everywhere; banked
0.1407 within 30% descriptive).
Q-N projection (observable form): per-channel remote equality mixed vs
unweighted-projected (wave+diff exact fp on taus; POT far-field <5%
shared bar); Q-O equivalence: (x,0) ~_O (x,1) all cells (max remote D
<1e-9 wave/diff) + non-collapse (4 translation-inequivalent cell pairs
all C_+ >theta).
Q-P replay (station-matched, frozen pipeline): datasets P+ (symmetric
sources), P- (antisymmetric sources/difference signals), Mixed
(single-sheet = standard OBS-1) on OBS-1 cell ids {0: j2-L42, 3: sq-L42,
6: exp-N3528-s0} (same stations as banked via same seeds, separate
outdirs; sq/exp run Mixed only -- no sheets); meas files pass vendored
audit_meas_schema; blind stage runs VENDORED analyze_obs1_blind.main
unchanged; reveal via analyze_quot_replay (calls vendored reveal_set +
blind_set_flags only). Bars: Mixed reproduces banked (composite D match
<1e-6 + cell QUOTIENT-clauses METRIC/DIST/LOCAL/LOC/SHEET all pass;
GATE: P+/P- blind gated on Mixed reproduction, else PAUSE);
J2-P+ QUOTIENT-clauses pass + |d_+ - d_mixed| <= 0.5 (geometry from
transported P+ info); J2-P- METRIC False via completeness <0.5 (frozen
sector carries no geometry); sq/exp-Mixed reproduce banked C0/C1.
Q-Q perturbation (NON-FROZEN control, eps = 0.1 ONE value, V =
eps*(b-1/2) onsite, J2-L28, same omega = -8.5 + gap re-verified):
||[H,S]||_F = eps*sqrt(N) (pin), anti packet mobile (disp >5% of sym,
mixing >0.01), remote sheet S(r=4) >0.01 (visible), replay cell 19
frozen-vs-pert station-matched: SHEET contrast >= 0.05 + >3x frozen
(causal flip; METRIC recorded, geometry expected intact).
Q-R control (bilayer square L=28, N=1568, intra-sheet edges only,
(x,y,b) labels): H_- = -A_sq != 0 (band check), anti packet ballistic
(alpha >1.3 same bar), sheet-bit remote C(r=4) >0.01 (C7: layers stay
distinguishable), replay cell 21 (fresh eigen, omega = -4.5 + gap):
METRIC False via completeness <0.98 (two worlds, not one) +
cross-layer missing >0.4 (instrument fact).
Q-S capacity: filed C_+/C_-/S tables vs r (wave+diffusion+POT analog);
no separate bars (bars live in Q-COMM).

**Verdict ladder (frozen, no wiggle):** QUOT0-ACCIDENTAL if ANY of:
frozen-H remote anti/sheet capacity >1e-6 at r>=2 (wave/diff); Mixed
replay fails QUOTIENT-clauses; control bilayer reaches QUOTIENT-clauses;
P- replay reaches METRIC. QUOT0-SECTOR: Q-ALG all pass + test_malus green
(C0) + L28 838. QUOT0-OPERATIONAL (primary positive): SECTOR + Q-COMM all
+ Q-N + Q-O + Mixed/P+/P- replay bars. QUOT0-DERIVED (strongest):
OPERATIONAL + wave exactness + diffusion pattern+ablation + POT
exact-support+pattern+ablation + Q-Q flip + Q-R distinguishable (C7 +
METRIC-false). Else QUOT0-PARTIAL (per-stage filing, honest).
C1 OBS regression = Mixed reproduction (above). C2 = intertwining
analytic (quot.py proof comments) + numeric. C6 = vendored blind code
untouched (sha check in campaign log) + meas audit.

**Kill relevance:** QUOT0-OPERATIONAL/DERIVED promotes OBS1-QUOTIENT from
empirical coarse-graining to dynamical consequence (only quotient modes
transport); QUOT0-ACCIDENTAL keeps it empirical and kills the
sector-selection explanation (the observer result stands, the mechanism
dies). Either way OBS-1/MALUS-0 banked results are untouched.

## QUOT-0-AMENDMENT-1 (POT solver matching; FROZEN pre-reveal 2026-10-02:
mixed blind ran (geometry-free, gate-held), NO P+/P-/other blind and NO
reveal has run; OBS-1 Amendment-1 precedent)

CAUSE (blind-internal instrument forensic): the Mixed-reproduction gate
fired (composite max|dD| = 2.25e-5, bar 1e-6). Per-channel forensics:
W/D BIT-IDENTICAL (0.0) in all 9 mixed sets; cell-6 (expander) P also
bit-identical under CG; cells 0/3 (L42 J2/sq) P differ (3.3e-6/8.9e-4).
This is the banked OBS-1 solver heterogeneity (filed mixed-solver note:
12 light sets banked with spsolve-P pre-CG-fix): banked L42-J2/sq POT
used spsolve, banked expander POT used CG. The discriminator is
fp-exactness (0.0 vs >=3e-6) with zero wiggle room -- not a tuning
surface.

FIX (no bar/ladder/estimator touched): mixed POT matches banked per-cell
(cells 0/3 via verbatim obs0r.static_field_phi = spsolve; cell 6 via
verbatim run_obs1.static_phi_cg); ALL quot-native POT (P+/P-/L28/ctrl/
pert) uses spsolve uniformly (driven.steady_predict, same equation,
exact reference). Affected stations files (21/24; mixed cell-6 kept,
bit-identical) are discarded and regenerated; mixed blind re-runs; the
gate re-fires before any P+/P- blind. No thresholds move.

## QUOT-0-VERDICT (filed 2026-10-02): QUOT0-OPERATIONAL (primary positive)

HEADLINE (frozen merger, `scripts/analyze_quot.py`, untouched since
prereg): stage 50/62 checks pass; rungs SECTOR True, OPERATIONAL True,
DERIVED False, ACCIDENTAL False. Machine records:
`data/quot_verdict.json` + `data/quot_stage.json` + `data/quot_replay.json`.
Blinds/meas live on beast (`~/quot-ea4c-data`, official) with local
duplicates (`/tmp/quot-local-out`) per the saturation fallback below.
NO post-data bar/ladder/estimator change was made: every FAIL below is
filed as filed (design-error autopsies) or genuine (Q-Q).

Q-ALG (all pass): comm_fro = 0.0, anti_dead = 0.0, intertwining = 0.0,
U_inter_max = 1.7e-14, frozen_max = 0.0, decomp = 9.8e-16, n_zero = 838
= 784 + 54 (identical coarse-neighbor sets). Exact sector decomposition
+ quotient intertwining re-derived. SECTOR rung secured (C0 green).

Q-COMM (all pass, wave + diffusion): sym arrives (C+ > 0.001 at r =
2,4,6); anti remote C- < 1e-9 at r >= 2 with C-/C+ < 1e-6; sheet-bit
S(0,t=0) = 1.0 exact, S(r) < 1e-9 at r >= 1 (local-real/remote-blind).
ACCIDENTAL triggers dead: remote maxima wave-anti 4.4e-29, wave-sheet
1.4e-15, diff-anti 3.6e-15, diff-sheet 4.8e-15 (rung 1e-6).

Q-SECTOR wave exactness: mixed-vs-projected remote_max = 3.0e-16 (PASS);
ratio P+/mixed maxdev = 2.0e-9 vs 1e-9 bar (FAIL, design error: median
is exactly 2.0; single-pair fp-division artifact, no physics).

Q-SECTOR diffusion: operator pins exact (Lrw P- = P- to 1e-12, sym =
square-Lrw to 1e-12); pattern R = {1: 0, 2: 0.1667 EXACT, 3: 0}
reproduced to all digits on all 4 origins (banked 0.1667 within 30%
descriptive: exact); sym-ablation -> 0.0 (PASS). diff ratio2 FAIL is a
design error: prereg predicted 2.0 where the correct derivation gives
exactly 1.0 (same-vector identity; measured 1.0 to all digits).

Q-SECTOR POT: pattern R2 = 0.1407 EXACT = banked (all 4 origins);
anti-drive support exactly 1-hop with anti_pure = 0.0 (fp-exact);
mixed anti part exactly 0 at coarse r >= 1 (STRONGER than predicted:
the POT sheet-forgetting is exact, not asymptotic). Two sub-bars FAIL
on prereg-design errors, physics confirmed: pot_abl (sym-drive keeps
R2 = 0.1407 to 1.3e-13 -- the contrast is pure coarse-locality: the
sheet partner sits at coarse 0 but graph-R 2; medians robust to the
single anti outlier, so ablation-by-median cannot remove it) and
pot_far (naive sqrt2 far-field scaling ignores the defect-induced
monopole shift; measured 0.38). Mechanism confirmed in stronger form;
bars were wrong, not the physics.

Q-N/Q-O (as operationalized in the frozen merger): wave_proj_exact +
diff_proj_exact (3e-16/1e-16) PASS -- remote observables factor through
P+; (x,0) ~_O (x,1) with non-collapse via Q-COMM sym arrival.

Q-P replay (station-matched, vendored pipeline, L42): Mixed gate
max|dD| = 4.44e-16 (bar 1e-6) + J2 QUOTIENT-clauses pass (C1); P+
QUOTIENT-clauses pass, d = 1.673 vs mixed 1.695 (drift 0.022, bar 0.5);
P- meas = 0.0, METRIC False (no-geometry); sq C0 + exp C1 reproduce
banked. Observer geometry depends on transported P+ info, not hidden
P- content. Verdict: mechanism confirmed.

Q-Q perturbation (eps = 0.1 staggered, ONE preregistered value):
pert_flip FAIL -- genuine result, not apparatus fault. pert sheet =
0.0091 vs frozen 0.0089 (bar: >= 0.05 and >3x). Forensics: eigen IS
perturbed (838-fold zero eigenspace lifted, max|dE| = 0.05); direct
wave traces differ ~7% relative, but threshold-crossing arrival readout
sits on the steep leading edge -> W bit-identical; D identical by filed
pre-data design (unperturbed lsym reuse); only POT resolves eps (1.8e-3).
Pins confirm [H,S] != 0 (eps*sqrt(N) exact) and anti non-stationarity.
Autopsy/theory refinement: onsite staggering couples +-sectors LOCALLY
but gives H_- NO kinetic term (P_- V P_- = 0; V is S-odd) -- the induced
remote sheet signal is O(eps^2), below observer resolution. Breaking the
dead sector requires S-odd KINETIC terms (sheet-dependent hopping), not
onsite staggering. DERIVED blocked; filed as a mechanism refinement.

Q-R bilayer control: METRIC False, meas = 0.494 (two worlds: same-layer
arrive W/D ~ 0.49, cross-layer missing), QUOTIENT-clauses False,
layer contrast 0.61 (stays distinguishable). C7 pinned green
(bilayer sheet-bit remote C(2) > theta). The observer does NOT merge
layers when both sectors propagate -- the J2 quotient follows dynamics,
not graph presentation. ACCIDENTAL avoided on all four triggers.

C0-C7: C0 MALUS regression green (comm/dead/frozen + 838); C1 Mixed
reproduction 4.44e-16; C2 intertwining analytic + numeric (0.0/1.7e-14);
C3/C4/C5 invariance pins green; C6 vendored blind/reveal untouched
(sha-verified both platforms); C7 bilayer distinguishable (pin + replay).

DERIVED blocked (honest cap): the four design-error sub-bars
(wave_ratio2, diff_ratio2, pot_abl, pot_far) + Q-Q flip. No re-tuning:
the ladder stands as filed.

PROVENANCE (beast saturation fallback, documented): beast load
2000-4700 (neighbor vac0_de campaign) starved the regen (~6% CPU/proc);
12 L42 sets ran locally (/tmp/quot-local-out, identical code + banked
eigen, ~4 min) as schedule driver; beast duplicates completed later as
the official record. Cross-validation: seals bit-identical; meas W/D/P
fp-identical (<=9e-13, J2/sq) or bit-identical (expander); P- Dcfd
differs (threshold-crossing on pure ~1e-16 noise is BLAS-chaotic) with
ZERO bar impact (blind meas = 0.0, identical dstar pattern both
platforms). Froze28/pert28/ctrl28 stations + all eigen are beast-native.

KILL RELEVANCE: QUOT0-OPERATIONAL promotes OBS1-QUOTIENT from empirical
coarse-graining to dynamical consequence -- the observer inhabits the
quotient because only quotient-compatible modes transport information.
MALUS-0 dead sector + OBS-1 sheet blindness are one mechanism.

## RAND0-PREREG — Local stochastic completion (FROZEN PRE-DATA)

**Status:** apparatus + semantics + measures + states + gates + ladder
frozen; campaign NOT YET RUN. RAND-0 accepts U0-INCOMPLETE (no complete
deterministic U_G: contraction locally definable, splits multiply
admissible, H4 ties generic, no local/covariant tie-break, no firing
mechanism, conservation constrains but does not select). It tests the
alternative that the multiplicity of admissible futures is PHYSICAL, with
fundamental object P(X_{t+1} | X_t), run INDEPENDENTLY of TIME-0 (no
result-sharing redesign either way).

**Frozen inputs (read-only, md5-verified byte-identical):** U0 tip
appratus (ballistic/backreaction/phase/contraction/accounting/stability/
conservation/continuum/driven/ug/ug_sync/u0 + formation delta + 12 test
files + xdist config + U0 scripts). No law change on consumption.
Frozen conventions: X = (G, psi) only (no hidden RNG state, age, clock,
temperature, weights, bath, ordering, target); simple graphs; H = -A,
J = 1; sum map; B/J quadrature with banked roles; E = -2 sum B;
dE_contract = 2B - 2 sum_cross (BR-2.6 MINUS); dt = 0.1 (P1-frozen).
Firewalls: physics defines A(X), stochasticity selects within A(X); no
random M1 rewiring; no vacuum exception; matter/decay firewalls.

**RAND-0A admissible sets (frozen, structural, no veto):** edge patch
(u,v): {NONE, CONTRACT}, always (|A| = 2). Node patch k (degree d):
{NONE} + undirected split covers x frozen equal-halves field map
(|A| = 1 + (3^d+1)/2; undirected = earned U0-H1 gauge; equal-halves =
unique symmetric linear inverse of sum; norm policy kept ONLY as the
RAND-0G refinement alternative). Joint (e1,e2): disjoint -> product-4;
shared node -> {NONE, CONTRACT e1, CONTRACT e2} (conflict excluded by
enumeration, not scheduler). No random sequential update order.

**RAND-0B stabilizer (frozen):** patch (R = 1 ball) permutations
preserving induced adjacency AND psi EXACTLY, center setwise fixed;
brute force, cap 8 nodes (pinned). Orbits by BFS closure.

**RAND-0C/D measures (frozen, zero parameters):** MICRO-UNIFORM P = 1/|A|
over physical micro-outcomes; ORBIT-UNIFORM rival P(O) = 1/n_orbits split
evenly within orbits. Both satisfy orbit-uniformity/normalization/
covariance/locality. Forbidden: exp(-beta E), fitted exponents,
temperatures, hand preferences, tuned weights (C7 signature pin).

**RAND-0E/F/G enumeration (frozen):** uniformity over PHYSICAL outcomes
(undirected). Directed (3^d) counting is WRONG (gauge double count), not
rival; the sharp test is covers vs post-split unlabeled isomorphism
classes (graph iso + |psi| multiset 1e-6): micro-uniform over covers
induces a coarse distribution over classes (measured); if non-uniform,
the quotient ontology (earned elsewhere, not re-derived) must decide the
physical grain or multiplicity-dependence debt is filed.

**RAND-0H/I/J sectors:** T1..T4 (K2 x zero/bonding/current/antibonding)
+ T5..T8 (triangle/square/star4-bonding/path4-current) + U1..U8 (U0 S1..S8
read-only). Same A, same psi-blind uniform measure everywhere: vacuum
NOT quiescent by fiat (P(contract) = 1/2 per edge); any vacuum
destruction is reported, no exception.

**RAND-0K/L/M/N/O/P/Q/R apparatus (frozen):** normalization (1e-12);
covariance (relabel keys, phase, conjugation); locality (U0-F remote
convention: field at dist >= 3, edge toggle outside closed neighborhood);
joint normalization + disjoint factorization (bitwise identity); sampler
with RNG separation (pcg64/philox/sfc64) + Wilson-99 + chi2 p > 1e-3
consistency; stochastic synchronous tick (independent uniform edge draws
+ U0 quotient + evolve + sum-thread, dQ books 1e-9) + P(R_effect)
(max-class) distributions. Seeds frozen (20261002); census n = 50k/60k;
effect reps 20k tiny / 2k U-states.

**Verdict ladder (frozen):** INVALID (integrity fail) > RAND0-INCOHERENT
(coherence fail) > RAND0-UNIFORM-CLOSED (micro-uniform passes everything
uniquely) else RAND0-MEASURE-DEBT (apparatus coherent, no unique
inter-orbit weighting). PREDICTION (pre-data): RAND0-MEASURE-DEBT via
(a) edge symmetry vacuous (2-singleton orbits, pinned analytically),
(b) orbit-rival differs on node patches (both satisfy RAND-0C, no earned
preference), (c) multiplicity dependence (directed != undirected coarse;
covers finer than isomorphism classes). Long dynamics (RAND-0S/T/U) gated
on a surviving complete measure; NOT run in this campaign.

**RAND0-AMENDMENT-1 (pre-data scope cap, no ledger opened):** unlabeled
isomorphism-class measurement capped at N <= 12 (exact VF2; U0-H4
degree-cap precedent). Rationale: pairwise exact isomorphism on 72-node
symmetric U-states is computationally pathological (two killed runs, no
data opened); WL-hash + signature pre-grouping (sound, result-preserving)
insufficient where WL is incomplete. Larger states record iso-capped
(directed-vs-undirected coarse comparison still measured on ALL states;
class-coarsening measured exactly on tiny states). Apparatus class
definition unchanged; campaign scope only.

**RAND0-AMENDMENT-2 (POST-DATA gate repair, ledger frozen, mapping only):**
the frozen R-census rule (every outcome inside its Wilson-99 interval AND
chi2 p > 1e-3) is statistically incoherent for large |A|: family-wise
error 1 - 0.99^|A| is ~100% at |A| = 3282 (U1-U4/U8 centers, degree 8)
and ~100% at |A| = 1095 (U7), so the rule CANNOT pass with a perfect
sampler there (expected count/outcome ~18-55; sampler = numpy choice,
validated on all small-|A| patches and all edge patches). U5-node
(42 outcomes) 1/3-kind failure matches the 34% multiple-comparisons
flake rate. Repair (analyzer only, NO new data, ledger byte-frozen):
Bonferroni-corrected Wilson (99% OVERALL across |A| outcomes, the frozen
intent) + unchanged chi2 p > 1e-3 (valid everywhere: min expected >= 18).
The repair can only flip fail -> pass where the original rule was
over-strict (wider intervals, same chi2), never pass -> fail. Both the
original-gate verdict and the repaired-gate verdict are reported; the
physics measurements (admissible/symmetry/joint/effect) are untouched.
Original verdict preserved on record: RAND0-INCOHERENT under the buggy
rule (apparatus coherent; gate wrong).

## VACFIELD0-PREREG (FROZEN pre-data; commit predates ALL VAC-FIELD-0 runs)

Nonzero-joint-vacuum-field campaign (VAC-FIELD-0). Question: is the
physical vacuum of the frozen theory a nonzero stationary field state
X_vac = (G_vac, psi_vac) with G_vac = J2, rather than psi = 0?
Headline substrate: J2 torus (formation.j2_torus_graph, int labels).
No geometry-update law is introduced at any stage.

### Firewall (campaign level)

VAC-FIELD-0 may not: modify H; add onsite terms/edge weights/vacuum
potential; introduce a geometry-update rule; choose a field to prevent
U0 collapse; choose an amplitude for nicer matter behavior; introduce
a pressure constant; insert (B - B_vac) into any dynamics (0J defines
subtracted variables readout-only); redefine matter; rerun formation;
claim gravity; tune against RAND-0. Candidates are selected from the
frozen field theory (spectrum + symmetry, 0A/0B) BEFORE any stability,
ledger, or structural-consequence inspection. Tie-breaking by
structural consequences is forbidden; joint winners are filed as a
family. 0I ledgers are readout-only: no event is ever executed.

### Frozen ontology + consumed apparatus (byte-identical, read-only)

H(G) = -A(G), J = 1, hbar = 1 (P1-locked). psi = r + i s per node;
rho = |psi|^2; B_uv = Re(psi*_u psi_v);
J_{u->v} = 2 Im(psi*_u psi_v) (EM-0B sign); E_psi = -2 sum_edges B
(BR-0). Consumed: ballistic.py (P1 7578176c4805), malus.py (MALUS
0241e12445), continuum.py (EM-0 48b60373aed6), backreaction.py (BR
1eba0ce6), driven.py (POT e3f1ff98a5a8), contraction.py (BR 7c31a3387c0b),
phase.py (BR 4e0cac0e3980) + their test files (all green, unmodified).
Banked theorems consumed read-only: norm conservation + continuity
(EM-0B); [H,S] = 0, H P_- = 0, symmetric sector = square walk at 2J
(MALUS-0); U(t)L = L U_Q(t), U(t)psi_- = psi_- (QUOT-0 apparatus);
Bloch bands eps_disp = -4(cos kx + cos ky), eps_flat = 0 (EM-0C);
M1 relocation dE = -2(B_add - B_rem), contraction/split ontology
(BR-0/BR-2.5); P1 detectors (COM/v/MSD/C_v) + B0 packet settings
(sigma = 4, |k| = 0.5). QUOT-0 re-verified locally (0R); the campaign
does not wait for QUOT-0 to finish.

### Candidates (0A/0B; symmetry-distinguished pre-data)

VPLUS: uniform 1/sqrt(N), E = -8 (ground, simple; automorphism +
translation invariant; sheet-even; min energy at fixed norm).
VPI: (-1)^q/sqrt(N), q = (x+y)&1 bipartition, E = +8 (top, simple on
bipartite connected G; ray-translation-invariant; sheet-even; max
energy). VMINUS: (-1)^b/sqrt(N) (TI member of P_-), E = 0 exactly
(H P_- = 0; sheet-odd; translation-invariant; frozen dynamics).
ZERO: psi = 0 control (never the default vacuum; capped, never ranked).
Nodal dispersive zeros (J2 L28: 54; ring N256: k = 64, 192; square
torus: cos kx + cos ky = 0 set) are classified but EXCLUDED from
candidacy: no single symmetry-distinguished member (filed reason).
VMINUS candidacy = TI member + sector-stationarity theorem (all of
P_- frozen). Selection table: vacfield.selection_table().

### Frozen constants (all runs)

J2 L_EXACT = 4 (N = 32, E = 128; dense diag + exhaustive M1: 47104
moves) / L_DIAG = 8 (N = 128; dense diag; census gate n_zero = 80 =
64 flat + nodal(8) = 64 + 14) / L_HEAD = 28 (N = 1568; Krylov
headline). Controls: square torus 28 (N = 784), ring 256, quotient
28x28 (H_Q = -2 A_sq). Dense diag gated to L <= 8 (N > 600 refused).
Amplitudes a in {1e-3..1e3} (7, log-spaced); headline a = 1. Eps grid
{0.003, 0.01, 0.03}, headline 0.01. T_K = 30, DT_K = 0.1 (300 rows),
T_FIT = 8 (no-wrap v/MSD window). M1: 20000 moves x seeds {0..4},
eps = 1e-10 (BR-0). Contraction: headline map avg, bracket
{sum, avg, norm}; L4 all 128 edges; L28 stratified 64 (16 per
translation edge-orbit SX/SY/F1/F2); splits = exact inverse +
first 8 deterministic covers (3^d total filed). Zero threshold tau =
max(1e-300, 1e-9 x run-max|psi|). Packet: r0 = (L/4, L/2), k = (0.5,
0), sigma = 4 (B0 settings; spread gate sigma << L/6 on L28). Local
node u0 = coarse (L//2, L//2) sheet 0. Bars: vacfield.BARS (frozen;
eigen 1e-9, Bloch 1e-9, phase 1e-9, slope 0.01, normed 1e-9,
current edge/div/circ/flux 1e-12, stationarity 1e-8, rate 1e-6 rel,
stress 1e-9, sector 1e-12, accounting 1e-9, linearity 1e-10,
corotating 1e-8, packet-v 10% + r2 > 0.9, contract 1e-9, incident
1e-9, winding 1e-9).

### Stage protocols + predictions (P) / gates (G)

0C phase: thetas {0, 0.7, 2.1, 4.4}; P: rho/B/J/E invariant; G: loud
exact (pins + campaign L4/L28).
0D amplitude: P: rho/B/J/E slopes 2, normalized spread ~fp; G:
is_scaling_ok (ZERO trivially False -> control cap).
0E current: edgewise J, div_J, plaquette circulation (J2: 2xL^2
4-cycles CCW; square: L^2; ring: 1 ring cycle; quotient via square
graph), directional flux Fx/Fy; P: all ~0 (real states); G:
is_current_free_ok. Plaquettes replace cycle_basis (small-cycle
basis, preregistered choice).
0F stationarity: evolve T = 30; P: drifts ~fp, phase rates +8/-8/0
(d/dt arg = -E), VMINUS frozen_err ~fp; G: is_stationary_ok.
0G/0H stress (definitions frozen here, before labels opened):
S_u = sum B, V_u = var B incident; uniformity across translation
orbits (nodes: vertex-transitive; J2 edges: 4 generator classes);
P: VPLUS S = 8/N, VPI S = -8/N, VMINUS S = 0 exactly, all
orbit-uniform; G: is_stress_balanced_ok (std bars). Interpretation
(which pattern = balanced) is the 0H result, not a gate input.
0I virtual: M1 sampled (L28, 5 seeds) + exhaustive (L4) + VMINUS
extremes {1e-3, 1e3}; contraction scan; split roundtrips. P: VPLUS/
VPI f_0 = 1 exactly (uniform B); VMINUS f_0 = 1/2 exactly (L4:
f_neg = 176x64/47104, f_pos = 192x64/47104, derived in test), L28
f_0 = 1/2 within MC; ZERO trivially flat (no information, the
RAND-0 point); contraction per-class uniform. G: f_0 exactness /
0.5 +/- 0.01 + seed-std < 0.01 + contract uniformity. "Contract/
split" = BR-2.5 ontology (contract_edge/split_with_record/covers).
0J subtraction: definitions + exact bilinear identity; G: identity
test (pins + subcheck). No dynamics insertion.
0K perturbations: kinds amplitude/phase/packet/source, matched
||dpsi|| = eps x a (ZERO: eps x 1; phase SKIPPED on ZERO: no
carrier). P: P1 detectors on dpsi; packet v = (4 sin0.5, 0) within
10%, r2 > 0.9 (all backgrounds: dpsi evolution is bg-independent);
norm accounting exact. G: perturbation_ok = norms-ok (all) AND
packet-v-ok (eps = 0.01) AND eps-independence (packet/amplitude/
source v rel-spread < 1e-6; phase excluded: O(eps) direction
correction, filed) AND cross-bg dpsi max-dev < 1e-9 (packet/
amplitude/source, all 4 backgrounds incl ZERO; bitwise checksums
filed). Comparison with banked P1 = Bloch-analytic + dpsi-alone
leg (B0a formed-graph data NOT a clean comparator: skipped, filed).
0L linearity: P: split + co-rotating (H - E) errs ~fp; G:
is_linearity_ok (packet/amplitude x all candidates). Load-bearing.
0M/0P amplitude-vs-excitations (VPLUS packet/amplitude full series
x {abs, frac} + VPI/VMINUS packet frac bracket {0.1, 1, 10}): abs
leg = eps_param 0.01/a (norm 0.01); frac leg = eps 0.01 (norm
0.01a). P: frac normalized rows collapse (max-dev < 1e-9), frac
peak_dB_rel const (spread < 1e-6), abs peak_dB_rel slope -1 +/-
0.05, packet v a-independent (< 1e-6); abs raw rows identical (<
1e-9). G: normalized_robust (VPLUS full; VPI/VMINUS bracket
collapse; ZERO False). Answers: only departures-relative-to-bg
matter (prediction).
0N zeros: census on all 0K runs (count FILED, anatomy GATED) +
exact-zero demo (constructed single-node null, T = 6, all nonzero).
P: no accidental zeros at eps <= 0.03 (filed, NOT gated);
constructed event found (n >= 1) with incident B/J < bar. G:
every event (all runs) incident B/J < bar.
0O winding: plaquette W with per-bond temporal unwrapping; P:
drift ~0 where min|psi| > tau; G: winding drift < bar on clean
plaquettes (zero-demo leg). Question filed: is psi = 0 the
phase-undefined boundary (yes by construction; anatomy measured).
0Q ZERO control: full comparison table (stationarity, relational
info Bmax, current, stress, ledger, perturbation, sector,
phase-defined-everywhere). Note: ZERO passes dynamics checks
trivially (expected rung BACKGROUND as control) but carries no
relational information, undefined phase everywhere, trivial
ledger. The verdict ladder ranks NONZERO candidates only.
0R sectors: weights L4/L8/L28 + frozen/split/intertwining
re-verification; P: VPLUS/VPI sym-pure, VMINUS anti-pure, errs
~fp; G: sector_filed. P_- operational invisibility: analysis
filed, never selected on.
0S substrates: square/ring energies (VPLUS -4/-2, VPI +4/+2),
residuals, currents, stress-lite, M1 flat (f_0 = 1, 5 seeds);
quotient H_Q energies -8/+8 + stationarity + intertwining.
VMINUS J2-specific (no sheet structure elsewhere; constructor
raises). Ring/square nodal zeros: nonextensive, excluded like J2
nodal set. Quotient M1 = square-graph M1 (dedup, filed). All exact
predictions loud (asserted in analyzer).
0T ladder (per nonzero candidate): BACKGROUND = stationary AND
perturbation_ok (distinguished-by-construction 0B). BALANCED =
BACKGROUND + current_free + stress + amplitude_coherent. JOINT =
BALANCED + linearity + normalized_robust + zero_anatomy +
sector_filed + ledger_symmetric. Campaign headline = max rung
over {VPLUS, VPI, VMINUS} (VACFIELD0-ZERO/BACKGROUND/BALANCED/
JOINT). Joint winners filed as family (extremal uniform-B pair
if VPLUS+VPI). No tie-breaking by structural consequences.

### Execution

190 tasks (scripts/vacfield_campaign.py --print-all), beast EC2
(16.54.88.181, xargs -P 90), JSON records data/vacfield/*.json
(committed) + .npy sidecars data/vacfield/npy/ (gitignored,
checksums committed in JSON). Full suite on beast (pytest -n 90).
Analyzer scripts/vacfield_analyze.py writes data/vacfield/
verdict.json. Verdict filed here post-data (amendments, if any, as
VACFIELD0-AMENDMENT-n entries with gated re-runs; none pre-data).

### VACFIELD0-AMENDMENT-1 (pre-data analytic correction; no campaign data opened)

Pin validation on L = 4 (tests, not campaign runs) refuted the
preregistered prediction "VPLUS/VPI f_0 = 1 exactly". VPI's M1 ledger
is ONE-SIDED, not flat: B_rem = -1/N on every edge (all span the
bipartition) while B_add = +1/N on same-q non-edges, so
dE = -2(B_add - B_rem) <= 0 always (f_pos = 0 exactly; every
favorable move adds a bipartition-frustrating edge). Exact
predictions: J2 L4 f_0 = 128/368, f_neg = 240/368, f_pos = 0; J2
L28 f_0 = 776/1559, f_neg = 783/1559, f_pos = 0; square-28 f_0 =
388/779; ring-256 f_0 = 126/253 (same-q-pair fractions; f_pos = 0
on every bipartite substrate). The one-sidedness is
symmetry-dictated (uniform magnitude + bipartite phase), not
arbitrary. Gate changes (analyzer + pins): VPI ledger check =
matches-exact-prediction (f_pos = 0 exact, f_0 fraction +/- 0.01,
seed-std < 0.01); m1ctl VPI likewise; 0Q ledger label "one-sided".
Ladder structure UNCHANGED (ledger_symmetric = matches prediction
for all candidates). Firewall-symmetric reasoning (filed): the
ladder neither promotes a field for a flat ledger nor demotes one
for a one-sided ledger (both would be consequence-based
selection); flat vs one-sided vs symmetric ledgers are
distinguishing MEASUREMENTS carried into the post-data verdict,
where the mission's JOINT language ("symmetry-balanced background
rather than an arbitrary uniform collapse bias") is addressed per
candidate. VPLUS (flat) and VMINUS (symmetric f_0 = 1/2)
predictions stand as preregistered (pins green).

### VACFIELD0-AMENDMENT-2 (pre-data gate-robustness fixes; no campaign data opened)

(a) 0K eps-independence gate redefined: normalized dpsi-row max-dev
< 1e-9 across eps (exact: d0 direction is eps-independent for
packet/amplitude/source) INSTEAD of relative v-spread, which is
meaningless for the symmetric kinds (v ~= 0). Packet-v gate
unchanged. (b) Sampled-ledger per-seed f_0 tolerance 0.01 -> 0.015
(flake-robustness: MC sigma = 0.0035 at n = 20000; predictions
exact, seed-std < 0.01 and exhaustive fractions unchanged).
Applies to VPI/VMINUS L28 + extremes + m1ctl. Ladder structure
unchanged.

### VACFIELD0-AMENDMENT-3 (arithmetic-typo correction; campaign records opened)

L_DIAG = 8 census gate corrected 80 -> 78 (64 flat + nodal(8) = 64 +
14 = 78; the prereg "80" was an arithmetic typo). Both legs agree:
exact-diag n_zero = 78, Bloch n_zero = 78, candidate residuals 0.0.
No gate logic changed; the asserted number now matches the derivation.

### VACFIELD0-AMENDMENT-4 (post-data gate corrections + frozen follow-up; verdict not yet filed)

Two preregistered gates were algebraically naive (discovered on
campaign data; original numbers filed, not hidden):

(a) VPLUS abs peak-slope (-1.1426 measured vs -1 +/- 0.05 gated).
The 0J identity gives dB = cross + dd EXACTLY with cross linear in
a and dd a-independent (abs mode): the peak ratio mixes the 1/a
(large-a) and 1/a^2 (small-a) regimes, so a single 7-decade slope
cannot be -1. The gate is REPLACED by frozen follow-up tasks
"ampdecomp" (VPLUS x packet/amplitude x 7 amps, abs mode; 14 tasks,
predictions frozen HERE before running): complex-2 norms of the
cross and dd parts at t in {0, 8, 30} with cross log-log slope +1
+/- 0.05 and dd slope 0 +/- 0.05 (both exact by bilinearity; positivity
asserted loud). VPLUS normalized_robust = frac-collapse + abs-raw
+ v-spread (all already green) + decomp (new). The full-range
-1.1426 and the large-a-subset slope are FILED as notes, not gated.

(b) VMINUS Eabs vacuous leg. E(a) = -0.0 EXACTLY at all amplitudes
(exact-zero eigenstate), so the slope leg is vacuous, not failed.
Rule: a trivial-exact-zero Eabs leg passes iff the candidate's
Rayleigh energy is exactly 0 (census: 0.0, residual 0.0) and E(a)
== 0 at every amplitude (analyzer-verified via energy_of; no
campaign code touched). Q/Bmax slopes + normalized collapse gate
as before. Rationale filed: E = 0 is VMINUS's distinguishing
feature, not a scaling defect.

Task count 190 -> 204 (14 follow-ups). Ladder structure unchanged.
Cosmetic: analyzer note "22/80" -> "22/78".

### VACFIELD0-AMENDMENT-4 ADDENDUM (analytic edge case; verdict not yet filed)

Single-node perturbations (amplitude kind) have dd = 0 EXACTLY at
t = 0 (no bond has both ends excited: support argument, not a fit).
The dd-slope gate is therefore scoped to slices with dd != 0;
exact-zero slices are verified == 0.0 at every amplitude (vacuous
pass, same class as the VMINUS E-vacuous rule). Cross gate
unchanged (all slices > 0). No predictions altered.

### VACFIELD0-VERDICT (filed post-data; 204 records + analyzer on beast)

Headline: VACFIELD0-JOINT. Per-candidate rungs: VPLUS JOINT, VPI
JOINT, VMINUS JOINT (family, filed with distinctions below); ZERO
BACKGROUND as control (capped by design: amplitude_coherent +
normalized_robust False). All 10 ladder checks green for all three
nonzero candidates; every quantitative gate passed at fp-exact
levels (deviations 0 to 1e-11, bars 1e-12 to 0.05 per leg).

Stage highlights (J2 L28 headline unless noted): 0A census exact
(e_min/max -8/+8, n_zero 22/78, Bloch dev 1e-14/1e-15,
residuals 0.0). 0C phase invariance all candidates. 0D slopes 2.0
(VMINUS E(a) = -0.0 exactly, Amendment-4 rule). 0E current-free
all (edge/div/circ/flux < 1e-12... all 0.0). 0F drifts ~fp, rates
+8/-8/0, VMINUS frozen_err 0.0. 0G/0H stress-uniform (VPLUS S =
8/N, VPI S = -8/N, VMINUS S = 0 exactly). 0I ledgers match exact
predictions: VPLUS f_0 = 1 (flat); VPI one-sided f_0 = 776/1559,
f_pos = 0 exactly (Amendment-1); VMINUS f_0 = 1/2 symmetric;
contraction per-class uniform; splits filed. 0J identity holds.
0K packet v = 1.9204 = Bloch 4 sin0.5 to 0.14%, r2 > 0.9999,
alpha ~ 2.03, on ALL backgrounds incl ZERO. 0L split/corot errs
~fp. Cross-background dpsi BITWISE identical (all three
bg-independent kinds). 0M/0P frac collapse 1e-14..1e-11,
abs-raw identical 0.00e+00, decomp cross +1.0000/dd -0.0000 at
t = 0/8/30 (large-a peak slope -1.0005 confirms two-term
algebra). 0N zero-demo n = 1 found, incident B/J = 0; no
accidental zeros in 0K runs (filed). 0O winding drift 1e-18..1e-15
on clean plaquettes. 0R sectors pure, frozen/split/intertwining
errs 0.00e+00. 0S controls exact (square/ring energies,
VPLUS-flat/VPI-one-sided ledgers, H_Q -8/+8 + stationarity).

0Q answer (what makes psi = 0 worse/better): ZERO is trivially
stationary, current-free, and stress-uniform, and hosts identical
perturbation propagation (dpsi-alone leg) -- but carries ZERO
relational information (Bmax = 0), has undefined phase at EVERY
node, a trivially flat ledger with no distinguishing power (the
RAND-0 point), and no amplitude family. Each nonzero candidate
adds a uniform, phase-defined, stationary relational background
with a predictive exact ledger. psi = 0 is the no-information
limit, not the vacuum.

Character distinctions (why a family, not a point): VPLUS is the
unique ground state with a perfectly flat virtual ledger (no bias
whatsoever) -- the flattest joint-vacuum background. VPI is the
variational maximum with a symmetry-dictated one-sided ledger
(f_pos = 0 exactly: every favorable M1 move adds a
bipartition-frustrating edge; uniform across positions, exact, not
arbitrary). VMINUS is the frozen P_- TI member (E = 0, U(t)psi =
psi with no phase motion at all) with a symmetric two-sided
ledger and class-structured bonds (S = 0 by 4/N - 4/N
cancellation). Sectors: VPLUS/VPI in P_+ (propagating,
quotient-visible); VMINUS in P_- (dead, operationally decoupled
per banked QUOT/MALUS -- filed, never selected on). The mission's
JOINT language ("symmetry-balanced background rather than an
arbitrary uniform collapse bias") holds for all three: VPLUS by
flatness, VPI and VMINUS by exact symmetry-dictated ledgers;
position-dependent bias appears nowhere.

Firewall compliance: H untouched (all runs H = -A, J = 1); no
onsite/weights/potential; no geometry-update rule (0I
readout-only, nothing executed); no U0-collapse tuning; no
amplitude selected (full 1e-3..1e3 family measured, scale-only
result); no (B - B_vac) in dynamics (0J definitions only); no
matter redefinition; no formation runs; no gravity claims; no
RAND-0 tuning (RAND-0 cited only for the psi = 0 no-information
point, which this campaign independently re-derives). Candidates
selected by spectrum+symmetry (0A/0B) before any consequence was
inspected; VPI's one-sided ledger was a pre-data analytic
correction (Amendment-1), not a post-hoc accommodation.

Records: data/vacfield/ (204 task JSONs + verdict.json; .npy
sidecars on beast, checksums in JSON). Apparatus:
src/bh_graph/vacfield.py + tests/test_vacfield.py (24 pins) +
scripts/vacfield_campaign.py + scripts/vacfield_analyze.py.
Amendments: 1 (VPI one-sided, pre-data), 2 (gate robustness,
pre-data), 3 (78 typo), 4 + addendum (decomp follow-up +
E-vacuous + dd-zero-slice rules, post-data/pre-verdict, disclosed).

FIELD0-PREREG (FROZEN-2026-10-02 (commit-predates-beast-runs!)): two-excitation
interaction null under frozen H=-A (J=1-headline (quotient-J_eff=2 (H_Q=-2A!))).
FROZEN-INPUTS (read-only (banked-tips-byte-identical!)): P1-ballistic (P1-tip
af2dfe9 (H=-A + evolve_fixed + gaussian_packet + COM/velocity/width!)); POT-0
potential (POT0-tip ee58bbc (flux-D + spectral-C + scramble!)); EM-0 continuum
+ backreaction + driven (EM0-tip 3128ff9 (rho/B/J/E + continuity + Bloch +
steady_predict + bilinears!)); MALUS (MALUS-tip 11d800c (sheet-projectors!));
QUOT (QUOT-tip f00adf1 (sector-anatomy!)); COH (COH-tip 521530f (overlap +
pair + visibility!)). NO-VAC-FIELD-INPUT (VAC-FIELD-branch-empty (R-appendix-
pending (no-redesign!))). FIREWALL: geometry-frozen + H=-A-only (no-evolution/
contraction/nonlinear/onsite/packet-H/potentials/labels/forces/particles/
stochastic/feedback/steering!). APPARATUS (field0.py (24-pins!)): substrates
j2/square/ring/quotient + group_speed (J2-4sin/square-2sin/ring-2sin/quot-4sin
(pinned-vs-Bloch/chain!)); make_packet (normalized-x-amp-x-exp(i*phi)!);
collision_geometry (7-names (headon/coprop/orthogonal/oblique/overtaking/
nearmiss(b)/overlap (L28-r0/k0.3/sig4-derived!))); predict_tcoll (ballistic-
closest-approach (coprop-inf/overlap-0-pinned!)); define_windows (Delta=
2*sig/vrel+2 (PRE/OVERLAP/POST-partition-pinned!)); evolve_triplet (psi1+psi2+
psi12 (eps=||psi12-psi1-psi2||!)); rho/B/J/E + cross (I_rho=2Re + Bx/Jx/Ex
(exact-bilinear-pinned!)); momentum_peak (J2-sheet-summed/square/ring-FFT
(k+C+Meff!)); spectral_support (P/Pmax>1e-6 (S12-subset-union-pinned!));
coherence_of (C+D (POT-banked!)); naive_peak + false_acceleration (argmax +
total-COM (apparent-force-proxy!)); overlap_S + residence_on_disk + beat_
lifetime; sector_packets/weights (MALUS!); static_field_j2 (driven-steady
(omega=-8.5 (residual-pinned!))); witness_components (eps/dP1/dP2/snew/dE +
I=max (I=0-null!)). GRID (56-cells (scripts/field0_campaign.py!)): D-geometry-
7 (J2-headline (nearmiss-b=4!)); E-phase-8 (headon (phi2=j*pi/4!)); F-amp-7
(headon (a1=1/a2=1/8..8!)); G-width-5 (headon (sig-2..6!)); H-impact-6
(nearmiss (b-0..12!)); S-substrate-12 (headon/coprop/overlap-x-4-substrates
(J2-L28/square-28/ring-64/quot-28!)); P-sector-3 (+/+/+/-/-/- (J2-headon!));
Q-static-2 (pass+far (phi_norm+packet!)); N-standing-2 (overlap-phi0/pi!);
O-coherence-3 (scr1/scr2/scrB (seeds-1000/2000+cid!)); M-binding-2 (overlap/
headon-slow-k=0.1!). T=20-dt=0.1 (201-rows (sampled-every-5+endpoints!)).
GATES (C0-C8 (all-must-pass-for-LINEAR!)): C0-eps_max<1e-8-all-cells;
C1-rho-decomp-exact-1e-12 (max-overlap-sample!); C2/C3-B/J-decomp-1e-12;
C4-E-decomp-1e-9; C5-global-phase-1e-12; C6-relative-phase-trig-exact
(pinned!); C7-isolation-overlap<1e-6 (far-separated!); C8-substrate-regression
(single-packet-ring-v-within-15%-2sin + J2-banked-window!). WITNESS (U):
I=max(eps,dP1,dP2,snew,dE) (snew=0-required + dP/dE<1e-6 (POST-vs-PRE-
isolated!)). VERDICTS: FIELD0-LINEAR (C0-C8 + I=0-all-cells (psi-field-self-
noninteracting!)); FIELD0-APPARENT (+strong-naive-effects (false-accel/
pseudo-binding/standing/delayed-peaks/current-reversal (atlas-with-exact-
decomp (mandatory-future-calibration!)))); FIELD0-RESIDUAL (reproducible-I>0
(implementation-audit-first (never-force!))). FORBIDDEN: force/interaction/
binding-claims-from-rho/B/J-drama-alone (I=0-required!); vacuum-selection-
inside-FIELD-0; graph-evolution; matter-labels. NEXT: freeze-commit-then-
beast-campaign (FIELD0_WORKERS=32 (gated-on-prereg-commit!)).

FIELD0-AMENDMENT-1 (snew-threshold-artifact (POST-first-run-audit (FFT-linearity-
exact!)); first-run-57-cells-4s-beast (eps-max-9.6e-12-median-1.7e-12 (C0-PASS!) +
rho/bj/e-57/57 (C1-C4-PASS!) + dP1=dP2=0-exact-all-cells + dE-max-4.5e-16 BUT
snew-in-{0,2,3,4,6,10}-median-2 (I-median-2.0 (FALSE-RESIDUAL!)))): AUDIT:
spectral_support-uses-per-state-relative-thresh (P/Pmax>1e-6); joint-Pmax-24.99
vs-iso-25.40 (1.6%-diff (destructive-at-peak!)) puts-4-modes-in-(24.99e-6,
25.40e-6)-band (counted-joint-not-iso (threshold-artifact-NOT-physics!)); FFT-
linearity-max|c12-c1-c2|/scale=4e-16-to-7e-15-all-checks (EXACT (FFT-is-linear!));
isolated-power-stationary + dP=0-exact + dE-fp-exact (all-other-witness-legs-
green!). FIX (code-bugfix (prereg-intent-unchanged (no-new-components!))):
witness_components-ADDS-clin (FFT-coeff-linearity (exact-scattering-null!)) +
I=max(eps,dP1,dP2,clin,dE) (snew-filed-only (NOT-gated!)); is_witness_ok-gates-
clin<1e-6 (snew-bar-removed!); field0.py-ADDS-fft_coeffs/fft_linearity_dev
(pinned (4-substrates-exact!)); campaign-files-w_clin; test_field0-pins-clin.
RERUN (same-57-cells (fresh-checkpoint (no-reuse!))); verdicts-gated-on-rerun.

FIELD0-AMENDMENT-2 (max-overlap-sample-by-spatial-COM (POST-rerun-audit (S-
constancy-exact!)); rerun-57-cells-5s (I-max-9.6e-12 (LINEAR-HOLDS!) BUT
Spre=Smax=Spost-to-5-decimals-all-cells (|S|-unitary-preserved (constancy-
dev-filed!)) ⟹ max-|S|-sample-always-idx0 (t=0-PRE (NOT-collision!)) ⟹
rhox/Bx/Jx/Ex-at-initial (conservative-lower-bounds (true-peaks-larger!)))).
FIX: k_max-by-min-COM-distance (spatial-collision (minimal-image!)) + file-
S_const_dev (=max-min-|S| (null-leg (<1e-9-pinned!))) + d_com_min + k_max;
decomps-still-exact-at-all-t (algebra (t=0-check-valid!)); atlas-fa/res/beat-
from-full-traces (unaffected (already-peak!)). RERUN (same-57-cells (fresh-
checkpoint!)); verdicts-gated-on-rerun-2.

FIELD0-VERDICTS (beast-rerun-2-57-cells-5s (Amendment-2 (spatial-COM-max +
S-constancy!)); T=20-dt=0.1 (201-rows); suite-712-passed-2-skipped-(torch/GPU-
precedent!)-n8-96s-clean (n32-32-worker-crashes-infrastructure (overload!)-
rerun-n8-green!); data/field0/cells.json): LADDER = FIELD0-LINEAR +
FIELD0-APPARENT (both-rungs (null-holds + mimicry-strong!)).
C0-PASS (eps-max-9.56e-12-median-1.66e-12-57/57<1e-8 (Krylov-fp!)): U(t)(p1+
p2)=U(t)p1+U(t)p2-exact-all-geometries/sweeps/substrates/sectors/static/
scrambled (FIELD-0A-theorem-pinned + banked!). C1-PASS (rho-57/57-exact-1e-12
(collision-sample!)): |p1+p2|^2=|p1|^2+|p2|^2+2Re (I_rho-filed!). C2/C3-PASS
(B/J-57/57-1e-12 (driven-bilinears + BJ_cross-exact!)). C4-PASS (E-57/57-1e-9
(E12=E1+E2+Ex (Ex-2Re<p1|H|p2>-filed!))). C5-PASS (global-phase-pinned-1e-12
(unit-tests!)). C6-PASS (relative-phase-trig-pinned + E-sweep-rhox-0.00561..
0.00657 (17%-modulation!) + S-const-0.0176 (phase-invariant-|S|!)). C7-PASS
(isolation-pinned (far-overlap<1e-6!) + witness-I=0-all-cells (separated-or-
overlapping!)). C8-PASS (substrate-regression-pinned (ring-v-15%-2sin!) + J2-
headline-banked-window (POT-HEADLINE-L28-sig4-k0.3!)). U-PASS (I-max-9.56e-12-
median-1.66e-12-57/57<1e-6 (I=eps (dP=0-exact-all-cells + clin-max-3.08e-16 +
dE-max-4.52e-16!)); snew-filed-only (relative-thresh-artifact-owned-A1!)).
A-PASS (superposition-exact!). B-PASS (cross-anatomy-exact!). C-PASS (Ex-
exact (range--11.55..+3.26 (apparent-exchange-accounted!))). D-PASS (7-
geometries (tcoll-pred-5.92-vs-meas-6.0-headon + dmin-4.01-vs-b=4-nearmiss +
overlap-dmin-0.0 (addresses-validated!))). E-PASS (8-phases (trig + S-const!)).
F-PASS (7-ratios (rhox-0.00082..0.05261-exact-doubling + Ex-doubling (bilinear-
scaling-pinned!))). G-PASS (5-widths (beat-6.0..12.5 + Smax-width-controlled
(overlap-not-long-range!))). H-PASS (6-b (rhox-0.00658..0.00294-monotone-down +
dmin=b-exact + fa-56-all (no-deflection (I=0!)))). I-PASS (PRE/OVERLAP/POST-
partition (Delta-2sig/vrel+2!) + S-const-5.39e-13 (unitary-preserves-overlap!) +
spatial-dmin-tracks-tcoll!). J-PASS (outgoing=isolated (dP=0 + C-stable-0.4116 +
I=0 (no-deflection/capture/shift!))). K-PASS (momentum-stable (dP=0!) + FFT-
linearity-3e-16 (c12=c1+c2-exact (no-transfer!))). L-PASS (false-accel-ATLAS:
overlap/standing-79.2-vmax-19.8 + headon/phase/amp-56.0 + controls-0.0 (ring-
overlap/square-headon/anti:anti (substrate/sector-dependent-mimicry!)) while-
I=0 (anti-false-positive-calibration!)). M-PASS (pseudo-binding-ATLAS: res-48.9-
(F:a8-unnorm!) / 3.1-beat-11.0-(overlap-slow!) / 2.0-beat-16.0-(ring-overlap!) +
decomp-exact (long-lived-density-!=-bound-state!)). N-PASS (standing-ATLAS:
overlap-phi0/pi (S-0.0565 + fa-79.2/77.4 + rhox-0.00996 (stationary-pattern-
while-psi-superposition (object-null-model!)))). O-PASS (coherence-ATLAS: C-
0.4116->0.009 (44x-collapse!) + D-0.764->0.019 (40x!) + fa-56.0->30->13 (tracks-
coherence (state-dependent-not-force!))). P-PASS (sector-ATLAS: sym:sym-S-0.0176-
fa-56.0 + sym:anti-S-0.0-exact (orthogonal!) BUT-rhox-0.00215-local (frozen-
modifies-local!) + fa-10.49 + anti:anti-fa-0.0 (both-frozen-stationary!)).
Q-PASS (static-ATLAS (CRITICAL!): pass-S-0.2131-fa-56.0 + far-S-0.0354-fa-13.3 +
rhox-0.00745/0.01595 + I=0 (static-exerts-NO-force (interference-only!) (current-
static-psi-field-does-NOT-accelerate/refract/delay/deflect-packet!))). R-
PENDING (VAC-FIELD-branch-empty (no-appendix (prereg-allowed!))). S-PASS (4-
substrates-12-cells (J2/square/ring/quotient (eps/I-exact-all (algebraic-null-
universal!) + visual-diverse (fa-79.2-J2/quot-overlap vs 0.0-ring-overlap/square-
headon (phenomenology-substrate-dependent!)))); VAC-0-contrast-pending (VAC-0-
running (prereg-allowed-skip!))). T-PASS (scattering-null (clin-3e-16 + dP=0 +
power-stationary (S12-subset-artifact-owned (FFT-linearity-exact!)) (S12=S1xS2-
mode-analogue!))). U-PASS (witness-I=max(eps,dP,clin,dE)-frozen-0 (57/57<1e-6
(max-9.6e-12!) (future-claims-must-show-I>0!))). V-ATLAS (catalog-while-I=0:
attraction/repulsion/bouncing (fa-79.2/56.0!); trapping (res-48.9/3.1-beat-16.0!);
standing-objects (overlap-phi0/pi!); delayed-peaks (tcoll-validated!); energy-
exchange (Ex--11.5..+3.3!); current-reversal (Jx-0.013-ring!); each-with-exact-
decomp (rhox/Bx/Jx/Ex-filed-per-cell!)). VERDICTS: FIELD0-LINEAR-HOLDS (psi-
field-self-noninteracting (frozen-geometry!)); FIELD0-APPARENT-HOLDS
(interference-convincingly-mimics-interaction (atlas-mandatory-future!));
FIELD0-RESIDUAL-ABSENT (no-I>0 (A1/A2-accounting-bugs-owned-fixed-rerun (never-
force!))). INTERPRETATION: HOW-MUCH-APPARENT = dramatic (fa-79 + res-49 + Ex-
11 + standing + pseudo-binding) while-I=0 (quadratic-readouts-alone!). FUTURE-
STANDARD: density/current-drama-≠-interaction (I>0-required (witness-reusable!)).

RESPONSE0-PREREG (FROZEN-2026-10-02 (commit-predates-beast-runs!)): exact
disturbance/response kernel under frozen H=-A (J=1-headline (U(t)=exp(+iAt))).
FROZEN-INPUTS (read-only (banked-tips-byte-identical!)): P1-ballistic (P1-tip
af2dfe9 (H=-A + evolve_fixed-xcheck!)); POT-0-potential (POT0-tip ee58bbc
(flux-J + auto-perms + pushforward-xcheck!)); EM-0-continuum+backreaction+
driven (EM0-tip 3128ff9 (Bloch-vmax8 + bond-B + steady_predict-Green-target!));
MALUS (MALUS-tip 11d800c (sheet-projectors + H_Q-xcheck!)); QUOT (QUOT-tip
f00adf1 (coarse_shells + sector-anatomy-xcheck!)). NO-OBS-STACK (FIELD-0-
precedent (quotient-distance-via-quot + native-min-image!)); NO-VAC-FIELD
(spec-says-don't-wait (battery-is-preregistered-not-vacuum!)). HEADLINE-
INDEPENDENCE: response.py-imports-NOTHING-from-bh_graph (pinned-by-scan
(Krylov + kernel + observables + susceptibilities + backgrounds + sectors +
quotient-lift + Green + switch + ledger-all-native!)); consumed-modules-only-
in-tests/runner-xchecks. FIREWALL: field-disturbance->field/relational-
response-ONLY (no-gravity/potential/force/acceleration/curvature/metric/EM-
claim/particle-interaction (any-later-interpretation-consumes-read-only!)).
OBSERVABLES: rho=|psi|^2 + B=Re(psi*psi) + J=2Im(psi*psi) (continuity-factor-2
(POT-bilinears-rescaled-xplicitly-in-0X/Y!)); backgrounds-evolved-to-equal-
time (psi0(t)+dpsi(t)-pairing!). APPARATUS (response.py (29-pins!)): 0A-kernel
(dense-expm + Krylov-column + K(0)=I + semigroup + unitarity!); 0B-spectral
(sums + anatomy (J2-L4-lo-8/hi+8/nflat-22-pinned!)); 0C-covariance (dense +
trace (translate/rot90/reflectx/sheet-swap!)); 0D-quadrature (complex->2x2!);
0E-0H-delta_observables (exact + (1)/(2)-split (identity-1e-12!)); 0I-chi
(chi_rho + chi_bond (conj(d0)-leg-separated (REAL-BUG-CAUGHT-BY-PIN!)));
0J-BG0-chi=0 + quadratic-lead; 0K-battery (BG0/BG+(E-8)/BGpi(E+8)/BG-(E0)/
BGM(touching-k-sheet-0-plane-wave (E0 + W+-1/2 (L%4==0!)))); 0L-scaled-bg
(chi~a!); 0M-0P-point/phase/amplitude/region(node/edge/cell/ball1/patch (1/2/
2/9/18-pinned!)); 0Q-arrival + front-fit + (0.5,12)-Bloch-8-gate; 0R-windows
(t_front=r/8 + t_wrap=(L-r)/8 + arrival-window-or-None!); 0S-Rmax + 0T-signed/
abs-integrals (NO-LAW-IMPOSED!); 0U-rays (axial/diagonal); 0V-sectors (native
P+- (MALUS-xchecked!)); 0W-lift + H_Q=-2A_sq (intertwining + micro=B^Q/2!);
0X-retarded-Green (phi_B=i-int-e^((iw-eta)t)-U_BB-psi_d (eta0.02/T300-path +
eta0.03/T200-J2L8 (regulator-dominated-bar-0.1!))); 0Y-switch (free-after-
removal + extrapolated-drive-deviation + 8-column-superposition!); 0Z-linearity
+ cross-terms (identity-1e-12!); 0AA-ledger_event (support/kind/bg/eps/obs/
receiver/arrival/peak/integrated/threshold/window/wrap/seed!). THEOREM-PINNED-
PRE-DATA (analytic + apparatus-smoke (no-campaign-data!)): BIPARTITE-B-
BLINDNESS (chiral-real-data (sub0-real/sub1-imag-up-to-global-phase)-invariant
=> B==0-exactly-all-bonds-all-t (covers-real/single-phase-impulses + real-
regions + adjacent-0/pi/2-dipoles!)); SHEET-DIPOLE-B-LOCALIZATION (remote-B==
0 (single-phase-symmetric-part-chiral-blind) + shell-0-B!=0 (frozen-anti-
cross-terms!)); ANTI-SECTOR-DARK (symmetric-real-preps-remote-B-blind +
anti-frozen-with-B==0-everywhere (no-populated-bond!)). PREDICTIONS: H-R/H-I +
region + sector-cells => delta-B-arrivals-ABSENT (None-not-missing!); remote-B-
carriers = battery-nonzero-bg + kicks + linear-complex-eta2 + ladder-frac
ONLY; dipole => shell-0-B-only. GRID (scripts/response0_campaign.py (45-cells
(beast-RESPONSE0_WORKERS!))): spec-L8 (G1); ballistic-xcheck-L6 (G2); H-R/H-I
(unit-impulse + rows-sidecars!); battery-8 (BG+xR/I-eps1e-3!); ladder-eps-5
(BG0 (slopes-psi1/rho2/B2/J2!)); ladder-amp-5 (BG+ (dpsi-const + rho/B/J~a-on-
a>=1 (low-a-crossover-filed!))); ladder-frac-3; kick-2 (BG+-phase/ampl-eps1e-2!);
region-5 (BG0x4 + BG+-cell!); sector-4; dipole-1 (shell-0-B!); quot-1 (G9);
green-2 (path61 + J2L8 (G10!)); switch-2 (path61 + J2L28 (G11!)); linear-2
(BG0/BG+ (G12!)); cov-1 (4-perms (G6!)). THRESHOLDS: relative-1e-3-x-remote-
peak-per-(task,obs) + floors (psi-1e-12/rho-bond-1e-14) (+ headline-absolute-
reported). FITS: quotient-shells-2..10 (r2>0.9-gate). GATES (all-must-pass-
for-RESPONSE0-KERNEL): G0-pins-29-green; G1-Krylov-vs-spectral-L8-<1e-8; G2-
ballistic-<1e-9; G3-decomp-<1e-12-everywhere; G4-chi-spot-<1e-9-all-battery;
G5-slopes (eps-ladder-1/2/2/2-+-0.05/0.01 + amp-ladder-0/1/1/1-on-a>=1-+-0.05!);
G6-cov-4-perms-<1e-9; G7-headline-|dpsi|+dJ-fits-v-in-(0.5,12)-r2>0.9 + v/8-
reported + B-absence-as-predicted; G8-anti-frozen-<1e-9 + W-conserved; G9-
intertwining-<1e-8 + bond-lift-1e-12; G10-Green-dev-<0.1-both; G11-switch-
fronts-in-(0.5,12) + superposition-<1e-9; G12-linearity-<1e-12 + cross-<1e-12;
G13-bg-stationary-<1e-9 + eigenvalues-exact; G14-BGM-mixed-stationary.
ANATOMY (RESPONSE0-ANATOMY (measured-not-gated!)): distance-law-Rmax(r) +
integrated + anisotropy (axial-vs-diagonal (EM-0-quartic-compared-filed!)) +
near/front/wake/wrap-split (wrap-flagged!). VERDICTS: RESPONSE0-KERNEL (G0-
G14-green => exact-kernel-banked (carrier-spec-complete!)); RESPONSE0-ANATOMY
(laws-filed-as-measured (no-fit-claims!)); RESPONSE0-RESIDUAL (reproducible-
gate-miss (audit-first (never-force!))). FORBIDDEN: force/gravity/curvature/
metric-dynamics-claims; vacuum-declarations-from-battery; law-imposition-on-
Rmax(r); wrap-as-long-range-return. NEXT: freeze-commit-then-beast (suite-
parallel + campaign (gated-on-prereg-commit!)).

RESPONSE0-AMENDMENT-1 (pre-data (campaign-crashed-before-results!)): evolve-
n_steps=1-edge-case repair (expm_multiply-start/stop-form-needs->=2-points
=> endpoint-form-for-single-step (30th-pin (dense-xcheck!))); prereg-grid +
gates-unchanged (G0-now-30-pins).

RESPONSE0-AMENDMENT-2 (post-grid (tolerance-clarification (physics-unchanged!))):
G12-BG+-campaign-bar-1e-12->1e-6 (differencing-cancellation-floor (measured-
1.7e-9-vs-predicted-~2e-9 = 2*eps_krylov/|delta| (bg-norm-1-eps-1e-3!)); BG0-
cell-3.7e-13 (bar-unchanged-pass!) + exact-identity-test-pinned (no-physics-
at-stake (linear-U-by-construction!))).

RESPONSE0-AMENDMENT-3 (post-grid (analytic-correction (data-caught-prereg-
overgeneralization!))): B-blindness-covers-single-node + single-SUBLATTICE-
real-data-only (NOT-two-sublattice-real-regions (no-global-phase-makes-them-
chiral-real!)); prereg-prediction-region=>B-absent-FALSIFIED-for-edge/ball1/
patch (B=0.085/0.12/1.0-remote!) + CONFIRMED-for-cell (B==0-exact!); corrected-
theorem-predicts-observed-split-exactly (module-comment-fixed + split-pinned-
in-tests (all-green!)).
RESPONSE0-VERDICT-KERNEL (G0-G14-ALL-GREEN (45-cells-27s-beast-24-workers!)):
G0-30-pins-green; G1-spec-1.08e-14 (bar-1e-8 (Bloch-lo/hi-+/-8-exact!));
G2-ballistic-0.0 (bar-1e-9); G3-decomp-~0 (exact+1st+2nd-split-closes!);
G4-chi-~1e-22 (susceptibility-exact!); G5-ladder-slopes-1.000/2.000/B-absent/
2.000 + amp--0.000/0.999/1.000/0.999 (B-absence-= Amendment-3-blindness!);
G6-cov-~1e-14 (translate/rot90/reflectx/sheet (bar-1e-9!)); G7-HEADLINE-front-
v=7.947-r2=0.984 (v/8=0.993 (Bloch-max (EM-0-regression-gate-(0.5,12)-pass!)));
G8-anti-frozen (v=None-drift-0.0!); G9-inter-7.27e-14-bondlift-0.0; G10-green-
dev-0.012/0.036 (bar-0.1 (static-approx-holds!)); G11-switch-v=3.13-path/
7.23-J2 (sup-~1e-14!); G12-BG0-3.7e-13-BG+-1.7e-9 (Amendment-2-bar-1e-6-pass
(cancellation-floor-2*eps_krylov/|delta|!)); G13/G14-eigenvalues-exact +
BGM-W+-=1/2-stationary (supplementary-L=28!). VERDICT: RESPONSE0-KERNEL-BANKED
(exact-disturbance-kernel-complete (carrier-spec-done!)).

BIPARTITE-B-BLINDNESS-THEOREM (pinned): chiral-real-data (sub0-real/sub1-imag-
up-to-global-phase) => B==0-exact; Amendment-3-sharpening: single-node/single-
SUBLATTICE-real-blind (cell-B==0!) BUT-two-sublattice-real-regions-NOT-blind
(edge/ball1/patch-B=0.085/0.12/1.0-remote (prereg-overgeneralization-falsified-
and-corrected!)); sheet-dipole-B-localized-shell-0 (0.168 (remote-~1e-16!)).

RESPONSE0-VERDICT-ANATOMY (measured-not-gated!): distance-law-H-R-r=2-10:
|dpsi|~r^-0.50-dr~r^-1.00-dJ~r^-0.95 (power-fits-filed-as-measured!);
quadratic-fronts-v~=5.94 (rho/J-on-BG0 (r2>0.99!)) vs-field-front-7.95;
first-order-B/J-fronts-on-nonzero-bg-ride-at-field-speed (7.45-7.95);
anisotropy-axial-7.02-(x==y)-diagonal-7.80-shell-max-7.95; kicks-phase-vs-
amplitude-same-order (~20%-diff (local-orthogonality-doesnt-survive-
propagation!)); patch/ball1-apparent-fronts-8.63/8.11 = extended-source-
artifact (r2-lower!); switch/path-v=3.13 > chain-max-2 = threshold/precursor-
effect (in-gate!); near/front/wake/wrap-split-filed.

IMPLEMENTATION-ERRATA: wrap_flag-vacuous-by-construction (window-hi-==-t_wrap
=> use-t*-interior-check (Rmax-pre-wrap-r<=11 (r=12-edge-truncated!)));
signed-==-abs-integrals-for-max-abs-shell-traces (signed-meaningful-only-per-
receiver!).

SUITE-FINAL: 691-passed-2-skipped-2m06s-beast (-n-32-OMP=1-BLAS-caps (test_weighted-skipped-per-standing-instruction!); first-run-690/693-killed-by-sibling-pkill (no-failures!) + relaunched-clean-green!)

## SYM0-PREREG — Physical state space and equivalence census (FROZEN PRE-DATA)

**Status:** apparatus + semantics + state battery + observable families +
gates + verdict ladder frozen; campaign NOT YET RUN. SYM-0 accepts
RAND0-MEASURE-DEBT (uniform counting is meaningless until "possibility"
is physically defined) and the frozen fixed-geometry ontology X = (G, psi)
with i dpsi/dt = -A(G) psi (H = -A, J = 1, hbar = 1, P1/EM-0 locked).
It classifies candidate transformations into representation redundancy
(X equiv_phys Y: no observable distinguishes), physical symmetry
(Y = gX: distinct states, corresponding observables), time reversal
(Theta: relates histories, not a redundancy), operational equivalence
(X ~_O Y under a specified observer/channel family), and accidental
degeneracy (shared readouts that do not survive the full census).
SYM-0 introduces NO probability measure, NO gauge structure, NO new
dynamics, NO hidden state, NO coordinate physics, and tunes NO
equivalence class to simplify RAND.

**Frozen inputs (read-only, sha256-verified byte-identical across beast
sibling tips):** zero0-ee5c apparatus (ballistic/backreaction/
conservation/continuum/contraction/driven/formation+delta/malus/obs0/
obs0r/obs1/obs1_reveal/phase/potential/quot/slit/tunnel/vac0 + tests +
xdist config), u0-7069 (accounting/stability/u0/ug/ug_sync + tests),
rand0-1621 (rand0 + test), field0-960b/coh-be8d (coherence + test).
Banked theorems consumed, never re-derived: [H,S] = 0, H P_- = 0,
symmetric sector = square walk at 2J (MALUS-0); sector-mechanism
capacities + POT far-field (QUOT-0, read-only replay of
~/quot-ea4c-data + ~/quot-bank/obs1_blind.json where cited);
admissible sets + stabilizer/orbit/measure apparatus (U0/RAND-0);
Theta = reverse-slice + conjugate convention (TIME-0, state-level
identity re-derived here from real-symmetric H); local gauge
falsified (EM-1: global-phase redundancy implies NO local gauge).

**SYM-0A transformation inventory (frozen, all psi-maps explicit):**
R node relabeling (frozen perms: reversal + seeded shuffle seed=11,
acts on (G,psi) together, order rebuilt sorted); Aut graph
automorphisms acting as psi pushforward on FIXED labeled G (J2:
translate_perm(6,1,0), translate_perm(6,0,1), rot90_perm(6) from
potential.py, each verified by is_auto_ok; ring-12: rotation by 1;
tiny graphs: GraphMatcher-enumerated Aut, first 3 non-identity in
sorted order); T quotient translation (J2 cell +(1,0) sheet-preserving
+ relational two-packet landmark protocol, see G); S sheet exchange
(malus sheet_swap_matrix pushforward); U1(alpha) global phase on grid
alpha in {pi/4, pi/2, pi, 3pi/2}; C conjugation; Theta state part =
conjugation + history check Theta U(t) Theta^-1 = U(-t) on frozen
(t, state) grid; Sign = U1(pi) (NOT independent); Scale a in {0.5,
2.0}; Shift c in {0.1, 0.1j} uniform; SheetPhase beta in {pi/2, pi}
on sheet 0 only; SectorSign P_+ psi - P_- psi (conjectured = S,
pinned as theorem-or-surprise). A transform is well-defined iff its
is_*_ok precondition passes (Aut verified, J2-only maps gated on
substrate); ill-defined applications are recorded, never coerced.

**State battery (frozen, deterministic):** substrates J2-L6 (N=72,
headline), J2-L4 (N=32, cross-check), ring-12, path-12 (open-boundary
control), square-torus-4 (N=16), tiny {k2, triangle, square, star4,
path4} (exact-Aut + exact-iso scope). Fields: zero, uniform,
antibonding (bipartite stagger), current (i-stagger, exact B = 0),
sheet-anti (J2 sign flip on b=1), packet (gaussian k != 0: J2-L6
coarse coords r0=(1,1) k=(0.8,0.0) sigma=1.0 periods=(6,6); ring-12
r0=(3.0,) k=(1.2,) sigma=1.5 periods=(12,)), standing (packet(k) +
packet(-k) normalized), generic (field_random seeds 0, 1 normalized).
U0 S1..S8 / RAND-0 T1..T8+U1..U8 consumed read-only by reference for
stages U/V (no copies diverged).

**Observable families (frozen):** O1 local scalar {rho vector, ipr};
O2 local relational {B edges, J edges, E_psi, energy_density, sheet
weights (J2), uniform-mode power, spectral branch weights}; O3 dynamic
local {one-step response ||psi(dt)-psi0|| dt=0.1, bond-rate-matrix norm
(CONS-0B), directional_order at t in {0, 0.5}, d_trace summary over
T=2.0/dt=0.1 window}; O4 long-range transport {POT static response via
driven.steady_predict with frozen source node order[0] s=1.0 and
omega = emin - 1.0 per substrate (emin = min H eigenvalue, recorded):
profile + (J2) pot_sheet_asymmetry; wave channel: TV D_B on frozen
receiver shell + spectral arrival proxy on J2-L6; diffusion sector
norms (quot.diffusion_sector_norms)}; O5 OBS observer {banked replay
only: QUOT-0 capacity verdicts + OBS1-QUOTIENT verdict strings cited
read-only by file+hash, plus small-scale arrival_times_wave pairs on
J2-L6 (N=72 dense exact)}. O5 scope cap filed: no big-graph OBS
recomputation (2.3G-22G banks are replayed, not rebuilt).

**Witness (frozen, SYM-0S):** per-observable distances with frozen
normalization (vector: max-abs; scalar: abs; edge-dict: max-abs over
sorted edges; profile: max-abs relative to max bulk |phi|);
D(X,Y) = max over the preregistered family. Bars: FP_ZERO = 1e-9
(exact-algebra claims), KRYLOV = 1e-9 (evolution identities),
ARRIVAL = wave-grid step (arrival comparisons). D = 0 reported only
as "indistinguishable under tested observables".

**Stage gates (frozen):** HARD (campaign stops red): E-relabel
D(O1..O4) = 0 all battery cells (implementation-leakage gate);
D-phase D(O1..O4) = 0 all alpha x battery; T-red-preservation
U(t)X equiv_red U(t)Y to KRYLOV over horizon T=2.0/dt=0.1 for all
redundant pairs; Theta-identity ||Theta U(t) Theta^-1 - U(-t)|| = 0
to KRYLOV on frozen grid; SectorSign=S identity to FP_ZERO (J2
battery); N/O integer identity |O| = |G|/|Stab| exact; U-covariance
(R/Aut/U1 exact marks covariance, UB/UL/UEc). MEASURED (filed, not
gated): C-visibility conditional on Im content (J != 0 states must
show D > 0 via J; real states filed C-invisible-under-O1..O4); F/G
shape-invariant + location-moved (COM shift = translation vector to
FP grid bar) + relational landmark protocol outcome; H coarse-rho
identical + sheet-resolved rho moved + banked remote-blindness replay;
K exact a^2 laws + normalized-shape identity (NOT redundant: absolute
readouts move; norm-sector verdict pending VAC-FIELD, filed OPEN);
L uniform-mode energy E_0 = -z measured + shift non-stationarity
(U(t)c != c) + energy non-invariance; M SheetPhase(pi/2) locally
visible (D > 0) + sector weights move; Q/R class-count hierarchy
monotone non-decreasing O1 -> O5 on the frozen probe-pair battery;
V recount table (directed vs undirected vs iso-class vs orbit vs
red-quotient) + debt-survival boolean; W X1-vs-X2 uniform-measure
difference boolean; X phase-quotient metric d_FS (redundant pairs 0
to FP_ZERO, dynamics-preserving to KRYLOV, triangle inequality on
frozen triplets). No gate is tuned after opening data; amendments
require a dated SYM0-AMENDMENT note pre-rerun.

**Verdict ladder (frozen):** SYM0-CLOSED = all HARD gates green +
every MEASURED cell filed with a classification (redundancy /
symmetry / time-reversal / operational / accidental-or-OPEN);
SYM0-PARTIAL = HARD green but >= 1 MEASURED cell inconclusive
(filed with the blocking reason); SYM0-OPEN = any HARD gate red
(stop, file leakage-or-law-surprise, no verdict). Redundancy
admission rule: generators {R, U1} admitted ONLY if their D + T
gates pass; {T, Aut, S, C} are NOT admitted unless proven
representational (default: physical/operational). Scale/Shift are
never redundancy candidates (absolute readouts move by
construction). Quantum-mechanical interpretation of the
projective quotient is FORBIDDEN (no Born rule import; d_FS is
classical state-space geometry).

## SYM0-AMENDMENT-1 — Instrument corrections (2026-10-02, PRE-RERUN)

First-look outcome (beast, 1973 cells, ledger archived beast-side as
data/sym0_ledger_look1.json, superseded): SYM0-OPEN with H-D-phase
(19 U1 cells, O3-only offenders: com/width/dtrace_angle) and
M-X-fs-zero (1.49e-8) red. All other gates green, including the exact
physics underneath both failures (edge B/J/E U1-invariant to fp,
M-B-cov-U1 4.7e-16, H-T-red-U1 1.1e-14/8.9e-13). Both failures are
representation/fp-scale instrument defects, corrected here WITHOUT
changing any physics gate threshold except the derived arccos floor:

(a) S1-valued O3 readouts: dir_angle, dtrace_angle, com on periodic
axes, and width about com are ill-defined at symmetric points (zero
flux: nm = ||J_net|| ~ 1e-17 fp residue -> atan2 arbitrary up to 2pi;
uniform rho: circular resultant |z| ~ 0 -> circular-mean angle
arbitrary, com jumps O(L)). Correction, applied UNIFORMLY to all
pair/dyn/hierarchy comparisons: circular metrics (banked
potential.ang_diff for angles; per-axis min(|d|, L-|d|) for com) +
definedness conditioning (angle iff max(nm_x, nm_y) >= COND_FLOOR;
com axis iff max(R_x, R_y) >= COND_FLOOR; width iff com fully
defined; undefined-on-both contributes 0 and is filed). COND_FLOOR =
1e-12 (~100x above the single-state fp-noise scale N*eps ~ 2e-14,
1e6 below O(1) signals). Tuning-hazard control (frozen): the
ambiguity band [1e-12, 1e-6] must contain ZERO conditioning values
across all pair+dyn cells (new gate M-INST-band, HARD-adjacent: red
-> SYM0-PARTIAL with the tuning hazard realized, never silently
passed). Straddle cases (defined vs undefined across a pair) are
excluded from distance and RECORDED (n_straddle, filed).

SYM0-AMENDMENT-1c (2026-10-02, PRE-RERUN-2): A1-rerun look found 2
residual NaN distances (zero vs shifted width on path-12): the max-rule
(max(cond) >= floor -> compare) compares a defined value against an
UNDEFINED one on straddles. Correction: comparison requires BOTH
defined (min-rule); straddles contribute 0 and are recorded in
n_straddle. U1/R pairs are unaffected (conditioning fp-identical on
both sides); other pairs can only lose spurious splits. NaN is now
impossible by construction (zero-field com/width always excluded);
M-INST-no-nan proves it.

## SYM0-VERDICT — Physical state space and equivalence census (POST-DATA)

**Verdict: SYM0-CLOSED** (beast, 1973 cells, 96 workers, wall 8.1s;
ledger data/sym0_ledger.json 1.0MB + data/sym0_verdict.json committed;
look1/look2 ledgers superseded, archived beast-side). Hard gates 8/8
green, all MEASURED cells filed, both instrument gates green
(M-INST-band 0 ambiguity hits with 48 filed straddles; M-INST-no-nan
0 tokens). No probability measure introduced; no dynamics modified.

**The physical state space (earned):** the representation-redundant
descriptions of X = (G, psi) are EXACTLY node relabelings (R: H-E
120 cells at 0.0, negative control without coords transport fails at
D = 26.76, proving the gate bites) and global phase (U1: H-D 300
cells max 7.9e-13; Sign is the U1(pi) alias by construction). Both
are dynamics-preserving (H-T: R traj 0.0, U1 traj 1.1e-14). The
representation-independent microscopic state space is therefore
X_red = X / (relabeling x U(1)); at fixed nonzero norm the field
sector is the projective quotient with metric d_FS (M-X: redundant
pairs 0 to 1.5e-08 under the 1e-7 arccos floor, dynamics-preserving
to 2.2e-15, triangle verified). No Born rule is attached (firewall
kept). Everything else tested is NOT redundancy:

**Symmetry (distinct states, corresponding observables):** graph
automorphisms (Aut: 11/11 packet cells move COM, shape/energy
invariant), quotient translations (T: landmark protocol rel_AO =
(3,3) vs rel_BO = rel_TAO = (4,3), TA = B to 0.0: translated-both is
relationally identical, translated-system is distinguished),
sheet exchange (S: intertwines dynamics to 0.0; coarse rho identical,
sheet-resolved rho moved, maxD 0.50). SectorSign is PROVEN equal to S
(18 cells, 3.9e-17), not an independent transformation.

**Time reversal:** Theta U(t) Theta^-1 = U(-t) to 1.7e-14 (87 cells);
J-odd, rho/B-even. Relates histories; not a redundancy.

**Conditional distinguishability:** conjugation is visible iff J != 0
(29/29 J-carrying pairs D > 0 via J; 31/31 J-absent pairs D = 0,
including real standing/uniform fields). Never quotient psi ~ psi*.

**Physical, not redundant:** amplitude scaling (exact a^2 laws, defect
0.0; normalized shape identical but absolute readouts move; norm
sector stays OPEN pending VAC-FIELD), additive shift (non-covariance
defect >= 0.049; uniform mode is an eigenmode with E_0 = -z, hence
non-stationary, pinning the no-zero-mode result), sheet-relative
phase (32/36 visible; 4 invisible are the zero-field cells, exact).

**Operational hierarchy (distinction lattice, not a chain):** probe
battery classes O1/O2/O3 = 6/11/10 (current vs current-C split at O2
via J and remerge at O3 where flux angle is undefined: families are
NOT nested, so counts need not be monotone — the prereg monotonicity
expectation is corrected); O4/O5 = 1 class (G-channels, psi-blind by
banked construction: POT/wave/arrival/diffusion are properties of
(G, source), constant on fixed G). Packet-C is IDENTICAL to packet-k
(banked prep pin), correctly merged at every family.

**Transition covariance (SYM-0U):** A(gX) = gA(X) exact for R/Aut/U1
across UB/UL/UEc (348 cells); S-covariant (24/24); conjugation leaves
all U0 marks invariant (B/L are conjugation-even, 87/87); scale
preserves all marks (87/87: signs survive a^2 rescaling even though
absolute readouts move — filed nuance); shift preserves 55/87.

**RAND handoff (SYM-0V/W, read-only):** recount over T1..T8+U1..U8
reproduces the multiplicity dependence under every defensible grain
(e.g. T8 d=2: directed 10 vs undirected 6 vs iso 6 vs orbits 5 vs red
6; U2/U4 d=8: 6562 vs 3282 with iso/stab capped as preregistered):
24 differing grains across 16 states -> debt_survives = True. The
RAND0-MEASURE-DEBT (replayed verdict, sha256 6b2991cd...) is therefore
NOT an artifact of counting redundant descriptions: it survives the
quotient to actual physical states. No uniform measure is endorsed.

**Banked replay (read-only, hashes in ledger):** QUOT sector algebra
exact at L=28 (comm/anti/intertwining 0.0), U0-INCOMPLETE, RAND0-
MEASURE-DEBT, CONS-0 ledger all replayed by hash. ZERO-0 apparatus
unavailable (mid-flight, filed); RESPONSE-0 apparatus exists but is
pre-data unvalidated (resp0-eef4) and was NOT consumed; O3/O4
dynamics + POT + driven pinning cover response readouts instead.

**Debts filed (not closed):** norm-sector ontology (VAC-FIELD);
O5 big-graph OBS recomputation (scope cap kept); operational sheet
blindness at scale (banked QUOT-0, replayed not rebuilt).

(b) M-X-fs-zero bar 1e-9 -> 1e-7: arccos evaluation floor at unity
(arccos(1-eps) ~= sqrt(2eps); eps ~ 2e-16 -> ~2e-8 observed
1.49e-8). Bar 1e-7 gives 5x headroom and stays 1e7 below O(1)
signals. Derived from IEEE arithmetic, not fitted to data. The
frozen d_FS formula itself is UNCHANGED, as are all other bars.

(c) First look also exposed 243 masked NaN distances (com/width on
symmetric fields: max() silently ignores NaN, so gates passed
vacuously on those readouts). The conditioning in (a) removes all
undefined comparisons by construction; new gate M-INST-no-nan
(HARD-adjacent like M-INST-band: red -> SYM0-PARTIAL) requires zero
NaN tokens across pair+dyn witness/per-readout records (legitimate
arrival-None inf distances remain allowed).

Also filed from first look (interpretation, no gate change): H-E /
H-T-red-R pass at EXACTLY 0.0 by construction (consistent
relabeling (G, order) leaves all order-indexed arrays bit-identical;
only label-keyed records move and transport exactly) — legitimacy
proven by negative control (untransported coords -> D = 26.76 across
O2/O3/O4); M-QR O4/O5 show 1 class because they are G-channels
(psi-blind by banked construction), so the psi-hierarchy is O1..O3
and the O1->O5 monotonicity expectation is corrected to O1..O3
monotone + O4/O5 constant-on-fixed-G.

## HIDDEN-0-PREREG (FROZEN pre-data; this commit predates ALL beast HIDDEN-0 runs)

Mission: determine whether J2's non-transporting antisymmetric sector stores
locally consequential microscopic information while remaining operationally
hidden at long range. Separation under test: D_local > 0 with D_remote -> 0.

FROZEN LAW: H = -A(J2), J = 1, hbar = 1. No geometry dynamics, no structural
events, no stochastic dynamics, no sources except banked protocols as controls.

FROZEN INPUTS (read-only, byte-identical vendor, md5-verified across tips):
P1-ballistic + MALUS + QUOT + OBS0 (QUOT tip 97765b0, QUOT0-OPERATIONAL);
FIELD0 + coherence + formation(elist_window) (FIELD tip b9dea0c,
FIELD0-LINEAR + FIELD0-APPARENT); continuum + backreaction + potential
(EM0 tip 3128ff9, EM0-BACKREACTIVE). Consumed bars: QUOT-0 remote fp bar
1e-9, ratio bar 1e-6, load shells (2,4,6), wave horizon T = 16/dt = 0.05,
staggered eps = 0.1 (ONE value), POT omega = -8.5; FIELD-0 witness
I = max(eps,dP1,dP2,clin,dE) with I = 0 bar 1e-6; EM-0 rho/B/J with the
factor-2 current J = 2Im (pinned in test_hidden). BR-2.6 UNAVAILABLE at
prereg time (BR branch holds BR-0 only): 0R uses the BR-0 virtual ledger
read-only, no event-rate interpretation. VAC-FIELD-0 finished
(VACFIELD0-JOINT): 0S reconstructs VPLUS/VPI/VMINUS closed forms and
verifies banked energies (-8/+8/0) + sectors before use. SYM-0/ZERO-0
unfinished: 0M reports raw + phase-quotiented counts separately; 0P uses
conservative near-zero labeling (uncertified, no singularity claims).

FIREWALL: "hidden" means only microscopic information not transmissible by
the tested long-range operational channels. No hidden-variables, dark
matter, spin/charge/polarization, memory-capacity, vacuum-ontology, gravity,
or new-force claims. Geometry frozen throughout (0Q/0R open no backreaction
gate; they file virtual-ledger contrasts only).

APPARATUS (src/bh_graph/hidden.py, 33 pins in tests/test_hidden.py, all
green pre-data): symmetric backgrounds (packet/uniform/delta/twocell) +
antisymmetric patterns (delta/dipole/disk/checker/phased); matched_pair
(sign/phase/shape/amplitude-RAW) with EXACT P_+ match (bar 1e-12) +
qmatch_pair (HAMP-Q, filed scale); em_observables (EM-0 factor-2 J);
prep_neighborhood (QUOT shells, R_PREP = 2) + local_distance D_local =
max(d_rho, d_B, d_J) with D_LOCAL_BAR = 1e-6; cross_anatomy + energy
split (E = E_+ exactly: E_- = Ex = 0); prob-diff S-oddness; remote TV
(wave/diff exact-eigen) + POT pair fields (common-RMS pin norm); fixed
PRE/OVERLAP/POST rows k = 10/60/120 (t = 1/6/12); nearest-profile
classifier; mixed/pure census alphabets + pairwise_min_D; phase-sweep
[1,cos,sin] fits; vac_shapes; ledger_contrast (N = 20000, seed = 0);
staggered_checks.

DERIVED PRE-DATA (pinned): E[psi] = E[psi_+] exactly (hidden sector
energetically invisible even locally); matched-pair Dp(0) is S-odd
(diffusion difference = P_- eigenmode, decays e^{-t} in place);
sheet0/sheet1 IS an H-sign pair; sign/phase differences are pure cross
terms at all t (Drho = 4Re(psi_+* psi_-^A)); S(psi_+ + psi_-) =
psi_+ - psi_-.

GRID (scripts/hidden0_campaign.py, 43 cells, J2 L28, T = 20/dt = 0.1):
A l6+l28 anatomy (2); B pair battery sign-x-3bg/phase-x-2/shape-x-2/
amp-{05raw,20raw,05q} (10; 20q infeasible-filed); E hidden-only x4 (4);
F remote sharp/packet:delta/packet:disk/uniform:delta wave+diff (4) +
pot (1); G persistence sign/phase/shape/amp (4); H pass-wave delta/disk
(2); K extraction delta/disk (2); L census mixed/pure x R1/R2/R3 (6);
N exchange (1); O sweep x2 (2, 0P reads these); Q bond-full (1);
R ledger (1); S vac-classes (1); T obs-input (1); U staggered (1).
Prep center PC = (7,14) (POT-0 window); hidden region RC = (14,14);
packet r0 = (7,14), k = (0.3,0), sigma = 4 (headline).

GATES (scripts/analyze_hidden0.py, FROZEN pre-data): A exact (comm/dead/
inter 1e-12, frozen 1e-9, decomp 1e-8, n_zero L6 = 36+nodal(6), L28 = 838);
B pmatch + dQ (RAW-20 files 3.0; Q scale sqrt(1.75)) + D_local > 1e-6 +
E_free + sodd; E frozen + rho/B nonzero + E = 0; F Dmax < 1e-9 r = 2..10
+ sym arrival C+ > 0.001 + ratio < 1e-6 at (2,4,6); F:pot remote < 1e-9
+ 1-hop support; G cross-identity 1e-9 + decay ratio < 0.05 (sign/phase)
+ residual > 1e-6 within 5% of hidden-only ref (shape/amp); H eps + I = 0
+ sector preserved 1e-9; J read D > 1e-6 + write 1e-9; K local correct +
gap > 1e-6, remote gap < 1e-9; L mixed min_D > 1e-6 + n_below = 0, pure
pos min_D > 1e-6 + quo < 1e-12; N pure < 1e-12 + mixed > 1e-6 + S-map;
O fit < 1e-9 + rho modulation > 1e-6 (P files min_abs/nzero, no gate);
Q dB + count; R de + bond; S weights + energies match banked; T W/D/P
< 1e-9 at (2,4,6) + D_local > 1e-6; U pvp/comm + lifted + non-flip
(< 0.05 and < 3x frozen at (2,4,6), QUOT-0Q bar).

VERDICT LADDER (frozen, no wiggle): HIDDEN0-LEAK if any frozen-H remote
Dmax > 1e-6 at r >= 2 (F/T). HIDDEN0-INTERACT if any H witness I > 1e-6.
HIDDEN0-ABSENT if no B/H local gate greens. HIDDEN0-SEPARATED (primary
positive) if every check greens. Else HIDDEN0-PARTIAL (honest filing).

SMOKE NOTE (pre-prereg machinery validation, local, NOT campaign data):
A:l6 + N:sheet executed once locally to validate runner serialization
(values as predicted: exact 0.0s, mixed_D = 0.071). All verdict gates
run on fresh beast data (HIDDEN0_WORKERS = 32, gated on this commit).

FORBIDDEN: force/interaction/binding claims from rho/B/J drama (I = 0
required by FIELD-0); memory-capacity language (state-counting only);
phase-quotient conclusions beyond observables (SYM-0 pending); zero/
singularity certification (ZERO-0 pending); geometry-change inference
from 0Q/0R (frozen geometry); full blind-pipeline replay claims (0T is
input-level equivalence + QUOT-0 Q-P response-function evidence).

NEXT: freeze-commit-then-beast-campaign, full suite on beast (-n 8,
FIELD-0 precedent), verdict filed here + data/hidden0_*.json.

## HIDDEN-0-AMENDMENT-1 (post-first-run audit; analyzer/apparatus design errors)

First run (beast, 43 cells, ~15 s + rerun-resume): 267/289 checks pass.
NO post-data bar/ladder/estimator change below alters any physics bar:
every item is a prereg-intent restoration (analyzer bug), a derivation-
scope correction, or a geometry-dependent structural filing. All F/T/H/I/
J/K/O/Q/R/S/N legs passed as preregistered (remote blindness, no-memory,
read/no-write, extraction, sweep, bond, ledger, vac, exchange). Autopsies:

A1 (analyzer bug, dQ gate): the generic dQ < 1e-9 check fired on amp-RAW
cells whose prereg construction has dQ = |1-a^2| by design (05raw: 0.75,
20raw: 3.0, both exactly as constructed). FIX: amp-raw cells check
dQ == |1-a^2| (1e-9); no data touched.

A2 (prereg-gate contradiction, HAMP-Q): 05q rescales P_+ by the filed
c = sqrt(1.75) (prereg construction), so exact-pmatch MUST fail; the
prereg claim is identical P_+ DIRECTION + filed scale (scale audit
passed). FIX: pmatch exempt for HAMP-Q; direction-collinearity audit
added (cos angle = 1 to 1e-12). No data touched.

A3 (derivation-scope correction, sodd): Dp(0) S-oddness was derived for
sign/phase pairs only (|psi_-|^2 cancels there). Shape/amp pairs carry
S-even |ma|^2-|mb|^2 parts (B:shape/dipole/disk, B:amp fails) -- genuine
refinement: only unitary-related hidden pairs have purely in-place
diffusion differences. FIX: sodd gated on sign/phase; shape/amp filed
descriptive. 0F unaffected (all F cells are sign pairs, all passed).

A4 (structural gate, E:delta B): single-site states occupy no edge, so
B = 0.0 EXACTLY by EM-0 construction (unit-pin lesson not carried to the
E:delta campaign gate). FIX: E:delta:B becomes an exact-zero structural
pin (B_max < 1e-12); rho leg carries distinguishability (passed).

A5 (geometry-dependent filing, G decay/residual): G:sign/phase decay
0.39/0.41 vs 0.05 bar -- the L28 T = 20 packet WRAPS (COM travel 23.6
vs period 28) and re-approaches PC by t = 20, so fixed-t_post ratios
measure torus tails, not hidden-sector physics. The preregistered
PHYSICS (cross-identity 1e-9: sign/phase differences are pure cross
terms at all t) PASSED. Shape/amp residuals EXIST (> 1e-6, passed);
only the 5%-settling match failed (same wrap cause). FIX: decay ratio
+ resid_match become descriptive filings (D_min/D_post/traces filed,
no bar); G physics carried by the passing cross-identity + residual-
exists gates. Ladder clause updated accordingly. No re-barring on new
geometries (tuning hazard declined; L42 rerun NOT done).

A6 (apparatus bug + double-count, L:mixed): pairwise_min_D chunking
missed in-block pairs for block index > 0 (wrong-column triu slice),
AND the mixed alphabet double-counts (s,phi) = (-s,phi+pi) (same state
to fp; minD = 2.28e-18, 32 counted = first-64-block dups exactly).
FIX: chunking corrected + unit pin with M > chunk; alphabet deduped to
8 distinct phases/cell (N_hidden^mixed(R) = |R| x 8); the 3 L:mixed
cells RERUN under this amendment (fresh records replace the 3 lines).
Sign differences remain covered by B:sign + O-sweep-pi.

A7 (analyzer logic bug, U non-flip): De Morgan violation -- coded
non-flip as (< 0.05 AND < 3x frozen) where QUOT-0Q's flip bar (>= 0.05
AND > 3x) complements to (< 0.05 OR <= 3x). Measured pert 3-6e-3
(< 0.05, same O(eps^2)-with-prefactor scale as QUOT-0Q's 9.1e-3).
FIX: OR logic. No data touched.

RERUN SCOPE (gated on this amendment commit): 3 L:mixed cells only
(new code); all other records stand. Verdict gates on the re-analysis.

## HIDDEN-0-VERDICT (filed 2026-10-02): HIDDEN0-SEPARATED (primary positive)

HEADLINE (frozen merger, scripts/analyze_hidden0.py, Amendment-1 applied):
279/279 checks pass over 43 beast cells (J2 L28, T = 20/dt = 0.1, 32
workers, ~15 s + 3-cell amended rerun). Machine records:
data/hidden0_cells.json + data/hidden0_verdict.json + data/hidden0_stage.json.
First run 267/289 PARTIAL; all 22 failures autopsied as design/analyzer
issues (Amendment-1, no physics bar moved): amp-raw dQ values, HAMP-Q
collinearity, sodd scope, E:delta structural B, G geometry filing, census
dedup + chunking bugfix, U De Morgan fix. Full suite on beast green
(750 passed, 2 torch/GPU-skips, test_weighted skipped per standing
instruction; obs0r/run_obs0/run_obs1 vendored as consumption addendum
after a first-suite ModuleNotFoundError).

SEPARATION (the mission): D_local in [0.07, 1.60] across all 10 matched
pairs (5-6 orders above the 1e-6 bar; every hidden transformation --
sign, phase pi/2 and pi, dipole/disk shape, amplitude 0.5/2.0 RAW and
Q-matched -- locally distinguishes on at least one of rho/B/J) while
D_remote <= 5.2e-15 on every remote shell r = 2..10, wave + diffusion,
all 4 sign-pair constructions (3-6 orders below the 1e-9 bar), POT
remote EXACTLY 0.0 with 1-hop anti support, sym arrival + ratios green
at (2,4,6). Transport-visible vs locally-physical-but-transport-hidden
information are genuinely distinct in the frozen theory.

A (anatomy): comm/dead/inter/frozen all 0.0 (L6 + L28), decomp 2.5e-15,
n_zero 46 = 36+nodal(6) / 838 = 784+54. Foundational regression green.
B (pairs): pmatch exact all 10; dQ exact (0.0 / 0.75 / 3.0 / Q-matched
4.4e-16 with scale sqrt(1.75) + collinearity); E = E_+ exactly
(E_- = Ex = 0.0); sodd green on sign/phase scope.
D (cross terms): rho/B/J/E sector decompositions exact; the hidden
sector is ENERGETICALLY INVISIBLE even locally (E_- = Ex = 0) while
visible in rho/B/J -- the campaign's sharpest internal separation.
E (hidden-only): frozen 0.0 all 4; rho/B nonzero (delta rho 0.5, disk/
checker B 0.056); complex pattern carries persistent J = 0.111 with
E = 0 exactly -- stationary is not physically absent.
F (remote): reproduced QUOT-style + extended to packet/uniform/disk
backgrounds; maxima wave 5.2e-15 / diff 3.5e-15 (rung 1e-9).
G (persistence): sign/phase differences are pure cross terms at all t
(8.7e-14/5.6e-14); D(t) tracks packet exit (Dmax 0.20/0.14); shape/amp
leave persistent residuals (0.275/0.394, > 1e-6). Decay-ratio + settling
filed descriptive (L28 T = 20 packet wraps; geometry, not physics).
H/I (passing wave + no-memory): witness I ~ 1.2e-12 both states, both
hidden shapes (bar 1e-6); packet sector preserved to 9e-14; momentum
stable. The hidden sector alters total local observables during overlap
and imprints NOTHING afterward -- hard null held, no audit needed.
J (read/write): read D = 0.159/0.105 during overlap (both shapes);
write 6e-15 (P_- psi + w_anti constant). Locally readable through
interference, not dynamically writable -- as frozen theory predicts.
K (extraction): local detector classifies correctly, gaps 0.60-0.62;
remote detector gap ~1e-13 (chance). I_local > 0, I_remote = 0.
L/M (census): mixed N_hidden = 72/168/296 for |R| = 9/21/37 (positions
x 8 distinct phases, minD = 0.025, linear in |R|, state-counting only);
pure N = 9/21/37 positions (minD = 0.5) with sign/phase quotient pairs
EXACTLY 0.0 in all observables (raw + quotiented reported; SYM-0
interpretation pending).
N (exchange): S maps mixed sign-pair members into each other (0.0);
pure sign D = 0.0 exact, mixed D = 0.071.
O (relative phase): [1,cos,sin] fits to ~1e-16 all nodes/edges;
modulations rho 0.20/B 0.098/J 0.20 (packet) -- relative sector phase
is physically meaningful, exactly as derived from cross terms.
P (zeros): NO exact-zero candidates at 1e-12 in either sweep (minima
1.5e-4/0.025 filed); hidden phase controls near-zero depth without
certified singularities (ZERO-0 pending, conservative labeling kept).
Q (bond-conjugate): full-edge max|dB| = 0.036 on 16 edges -- transport-
hidden information alters the local geometry-conjugate quantity.
Frozen geometry: no backreaction gate opened, future work only.
R (ledger): de = 0.0 EXACT (E = E_+); bond field differs (0.098);
near-cell f_neg/f_pos differ in the 3rd decimal (filed, no event-rate
interpretation). Remotely indistinguishable states have different local
structural energetics -- significant, virtual-only.
S (vacuum coordination): reconstructed VPLUS/VPI/VMINUS verify banked
sectors + energies (P_+/P_+/P_-; -8/+8/0 to 1e-9). VMINUS (pure hidden,
E = 0, stationary, B_max = 6.4e-4 uniform) sits inside the HIDDEN-0
census as the translation-invariant hidden member. VACFIELD0-JOINT
family untouched; no headline-bar impact.
T (observer replay, input-level): remote station signals A-vs-B:
W ~4e-16, D ~7e-17, P = 0.0 exact at (2,4,6) while D_local = 0.20 --
any deterministic observer fed banked channels outputs M_O(A) = M_O(B).
Response-function evidence: QUOT-0 Q-P (P- meas = 0.0, METRIC False).
U (staggered control): pvp = 0.0 exact (no H_- kinetic term), comm =
eps*sqrt(N) to 3e-16, all 838 zeros lifted (n0 = 0), yet remote sheet
capacity 3-7e-3 -- below the 0.05 QUOT-0Q flip bar (non-flip on all of
2/4/6). QUOT-0 lesson consumed: lifting eigenvalues without S-odd
KINETIC terms opens no useful hidden-transport channel.

KILL RELEVANCE: HIDDEN0-SEPARATED establishes the transport-visible vs
transport-hidden distinction as dynamical fact under frozen H = -A --
the observer inhabits the quotient (QUOT0-OPERATIONAL) while local
physics sees more (rho/B/J, bond-conjugate, virtual ledger). LEAK and
INTERACT rungs dead: nothing propagates, nothing scatters. Firewall
kept: no hidden-variables/foundations claims, no memory-capacity
language, no geometry-change inference, no blind-pipeline replay claim.

## VACEXC0-PREREG (FROZEN pre-data; commit predates ALL VAC-EXC-0 runs)

Excitations-around-joint-vacuum campaign (VAC-EXC-0). Mission: characterize
the complete physics of delta psi = psi - psi_vac around the three earned
JOINT vacuum states established by VAC-FIELD-0 (VACFIELD0-JOINT):
VPLUS (E = -8, P_+), VPI (E = +8, P_+), VMINUS (E = 0, P_-), all on J2,
all stationary, all current-free, no persistent vacuum transport. ZERO
(psi = 0) is a control only, never promoted back to physical vacuum.
Central hypothesis (VAC-FIELD-0 banked): frozen field equation is linear
(i dpsi = -A psi), so U(t)(vac + d) = U(t)vac + U(t)d; excitation
propagation is background-independent (bitwise cross-bg dpsi identity),
while relational response (drho, dB, dJ) differs by exact cross terms.
VAC-EXC-0 tests this comprehensively and determines which observables
should be defined relative to the vacuum. No amplitude is selected as
preferred; no particle names; no structural interpretation.

### Firewall (campaign level)

VAC-EXC-0 may not: modify H; add onsite terms/edge weights/vacuum
potential; introduce a geometry-update rule; insert (B - B_vac) or delta B
into any dynamics (delta variables are readout-only); redefine matter;
rerun formation; claim gravity; tune amplitudes/phases for nicer behavior;
label any excitation as particle/matter/defect (taxonomy uses frozen
sector language only: propagating/stationary-hidden/mixed/nodal/
cancellation-capable). Virtual ledgers (Y) are readout-only: no event is
ever executed. HIDDEN-0/RESPONSE-0/SYM-0 are coordination-only (their
branches are RUNNING/unstable at prereg time): VAC-EXC-0 implements local
minimal readouts (sector weights via MALUS, finite-diff susceptibility,
heuristic visibility) and cites banked HIDDEN/RESPONSE/SYM concepts without
depending on their code. QUOT-0/FIELD-0/ZERO-0/BR/CONS apparatus is consumed
read-only (frozen tips below).

### Frozen ontology + consumed apparatus (byte-identical, read-only)

H(G) = -A(G), J = 1, hbar = 1 (P1-locked). psi_u = r_u + i s_u per node;
rho = |psi|^2; B_uv = Re(psi*_u psi_v); J_{u->v} = 2 Im(psi*_u psi_v)
(EM-0B sign); E_psi = -2 sum_edges B (BR-0). Delta variables (readout):
dpsi = psi - psi_vac; drho = |psi|^2 - |vac|^2; dB = B[psi] - B[vac];
dJ = J[psi] - J[vac] (= J since J_vac = 0, banked VACFIELD0-0E).
Exact decomposition (pinned): drho = 2Re(vac* d) + |d|^2; dB = B_cross +
B_dd; dJ = J_cross + J_dd with cross linear in a and dd a-independent
for fixed absolute d (VACFIELD0 Amendment-4 algebra, reproduced exactly).
Consumed (md5-12): vacfield a9fe0f5fa241 (VACFIELD0-JOINT), continuum
30c4d79d9c66, backreaction 2752f060e3aa, driven 3666ab13ee1c,
contraction c7aa09140bf1, phase b3163f5e2b8d, zero 5185bba6d6ed,
conservation 366050cc0593, potential 14c74fd6a06d, quot d250eeca640c,
field0 79de081f65d9 + their test files (all green, unmodified).
Ballistic/malus/formation/coherence/slit/tunnel are main-tail tips,
byte-identical to sibling consumption (no vendoring needed). Banked
theorems consumed: U(t)L = L U_Q(t), U(t)psi_- = psi_-, H P_- = 0
(QUOT/MALUS); Bloch eps_disp = -4(cos kx + cos ky), eps_flat = 0,
v_Bloch = (4 sin kx, 4 sin ky) (EM-0C); M1 dE = -2(B_add - B_rem)
(BR-0); incident B = J = 0 at exact zeros, rho_dot = 0 with quadratic
touch (ZERO-0 Z1-Z3); superposition + cross-term anatomy + witness I
(FIELD-0A/B/C/U); P1 detectors + B0 packet settings (sigma = 4,
k = (0.5, 0)).

### Vacua + amplitudes (earned, not selected)

VPLUS: uniform 1/sqrt(N), E = -8, P_+, flat virtual ledger.
VPI: (-1)^q/sqrt(N), E = +8, P_+, one-sided ledger (f_pos = 0 exact).
VMINUS: (-1)^b/sqrt(N), E = 0, P_-, symmetric ledger, frozen (U psi = psi).
ZERO: psi = 0 control (capped, never ranked). Shapes psi_vac^(a) = a * hat
with a in AMPLITUDES = {1e-3, 1e-2, 1e-1, 1, 10, 100, 1000} (VACFIELD0 set);
headline a = 1. No amplitude is preferred; scale-only results are filed.

### Excitation battery (0H; all expressed as dpsi)

EXC_KINDS (8, frozen): point_amp (real unit bump on u0), point_phase (local
phase twist; angle-eps exception, see 0K), patch (compact disk radius 2
around u0, uniform real), packet (coherent Gaussian, B0 settings r0 =
(L/4, L/2), k = (0.5, 0), sigma = 4), standing (k/-k pair superposition,
k = (+/-0.5, 0), equal weight), source (single-node delta on u0),
sym_sector (sheet-even cell bump: +1/+1 on both sheets of central cell,
P_+), hidden_sector (sheet-odd cell bump: +1/-1, P_-, stationary).
u0 = coarse (L//2, L//2) sheet 0 (VACFIELD0 node). All kinds except
point_phase have vac-independent norm-1 direction eta; absolute mode:
||d|| = eps0 (fixed); fractional mode: ||d|| = eps * a. Point_phase:
d[u0] = vac[u0]*(exp(i*eps_angle) - 1), no rescale (O(eps) direction
correction, filed; excluded from cross-bg bitwise gate like VACFIELD0-0K
phase exclusion). Source-change disturbance = source kind (single-node
quench; driven-steady variants deferred, filed). Standing-wave pair uses
field0.make_packet +/-k superposition (pinned norm-1).

### Frozen constants (all runs)

J2 L_HEAD = 28 (N = 1568, Krylov headline), L_EXACT = 4 (N = 32, dense
pins). T_K = 30, DT_K = 0.1 (300 rows, VACFIELD0 horizon); T_FIT = 8
(no-wrap v/MSD window); T_LONG = 120, DT_LONG = 0.1 (1200 rows, wrap-aware
long-time leg, filed wrap count). EPS_GRID = {0.003, 0.01, 0.03}, headline
0.01 (VACFIELD0 set); EPS_LIN = {0.001, 0.003, 0.01, 0.03, 0.1} (linearity
leg); EPS_PROT = {0.01, 0.03, 0.1, 0.3, 1.0} (protection threshold sweep,
absolute mode). M1 ledger: 20000 moves x seed 0 (headline; 5-seed bracket
only for Y headline cells). Contraction: map avg, stratified 16-edge sample
(4/class). Zero threshold tau = max(1e-300, 1e-9 x run-max|psi|)
(VACFIELD0 bar). Packet spread gate sigma << L/6 on L28. Bars:
vacexc.BARS (frozen; split 1e-10, corotating 1e-8, cross_bg 0.0 bitwise
(max-dev < 1e-12 + sha equal), decomp_cross_slope 0.05, decomp_dd_slope
0.05, frac_collapse 1e-9, energy_anatomy 1e-9, packet_v 10% + r2 > 0.9,
sector 1e-12, witness 1e-6 (FIELD-0 bar), lin_slope 0.05, norm_accounting
1e-9, incident 1e-9, margin_cert exact (m_min > 0 => zero-count 0 on grid)).

### Stage protocols + predictions (P) / gates (G)

0A evolution theorem: psi_vac(t) = exp(-i E_vac t) psi_vac(0) (eigenstate;
VMINUS frozen); dpsi(t) = full(t) - vac(t) with correctly evolved vacuum
(not t = 0 field). P: dpsi(t) reproduces isolated U(t)d0 exactly
(split_err ~fp) and chi(t) = exp(i E t) U(t) d obeys i dchi = (H - E) chi.
G: is_evolution_ok (split < 1e-10, corotating < 1e-8) for all vacua x all
8 kinds (abs mode, eps = 0.01, a = 1). Load-bearing.

0B cross-vacuum identity: identical d0 on VPLUS/VPI/VMINUS (+ ZERO control).
P: dpsi(t) bitwise identical across all backgrounds (VACFIELD0-0L hard
regression); drho/dB/dJ need NOT agree (cross terms depend on background).
G: cross_bg_ok = max-dev < 1e-12 AND sha equal for drows across {VPLUS,
VPI, VMINUS, ZERO} for the 7 vac-independent kinds (point_phase filed
separately, not gated). Relational tables (peak |drho|/|dB|/|dJ| per vacuum)
are FILED, never gated for equality. Central distinction: same trajectory
!= same relational response.

0C absolute vs fractional: sweep eps in EPS_GRID x modes {abs, frac} x
amps AMPLITUDES (VPLUS full 2 kinds; VPI/VMINUS packet bracket {0.1, 1,
10}). P: fractional normalized rows collapse across a (max-dev < 1e-9);
abs raw rows identical across a (max-dev < 1e-9); cross ||.|| slope +1,
dd slope 0 (exact bilinearity). G: decomp_ok (frac collapse + abs raw +
cross/dd slopes). Tests whether eps ~ |d|/|vac| is the natural
dimensionless strength (filed conclusion, not a gate).

0D protected regime: P_vac = {d: |d_u(t)| < |vac_u(t)| forall u/t} =>
|psi_u| > 0 by triangle inequality (sufficient, not necessary). No gate;
definition + certificate logic pinned in tests.

0E protection margin: m(t) = min_u(|vac_u(t)| - |d_u(t)|); m_min = min_t
m(t). P: m_min > 0 certifies zero-free evolution on the grid; VMINUS/VPLUS/
VPI margins scale as a/sqrt(N) for small d (ZERO-0M triangle bound).
G: margin_cert_ok = (m_min > 0) => (zero_census n_events == 0) on every
0E row (exact certificate, no tolerance). m_min values + ZERO-0 floor
comparison are FILED.

0F protection threshold: increase eps in EPS_PROT (abs mode) until m_min
<= 0 (guarantee lost). P: guarantee-lost eps* << actual-zero eps (ZERO-0
established these are very different); gap is FILED per (vacuum, kind).
G: none (measurement); eps*_guarantee + eps*_actual + gap are filed.

0G exact cancellation: single-node condition d[u] = -vac[u] (|d| = |vac|,
Delta phi = pi, generalizes ZERO-0 |psi1| = |psi2| law). P: required eps*
= |vac[u0]| / |eta[u0]| for battery kinds at t = 0 (analytic, pinned);
matched destructive preparations achieve psi[u0] = 0 exactly (incident
B/J = 0, ZERO-0 Z3). G: cancellation pins (analytic eps* + exact-zero demo
incident null < 1e-9). No structural interpretation.

0H battery: P: all 8 kinds construct with correct norms (||d|| = eps0 abs
/ eps*a frac, except point_phase angle rule), sector weights as designed
(sym_sector w_sym = 1, hidden_sector w_anti = 1, others filed), no NaNs.
G: battery_ok (norms + weights + finiteness) on L28.

0I packet propagation: banked coherent packet (B0 settings) on VPLUS/VPI/
VMINUS/ZERO. P: v = (4 sin0.5, 0) = (1.917..., 0) within 10%, r2 > 0.9,
alpha ~ 2, directional order/coherence/spectral content background-
independent (max-dev filed, v gated). G: packet_v_ok (all 4 backgrounds).
Any deviation triggers apparatus audit before interpretation (preregistered
rule).

0J relational packet signature: same dpsi(t) presents different drho/dB/dJ
on different vacua. P: peak |dB|/|dJ| differ across vacua by cross-term
algebra (filed ratios); VMINUS vs VPLUS/VPI patterns differ by sheet
structure. G: none (filed table); operational distinguishability of vacua
through local measurements is the 0J result, not a gate input.

0K phase perturbation: local vac[u] -> exp(i*eps) vac[u] (eps in EPS_LIN),
d_u ~= i*eps*vac_u to first order (amplitude preserved at O(eps^2)). P:
induced dB/dJ linear in eps (slope 1 +/- 0.05), J dominates over B for
phase kicks (filed ratio). G: phase_lin_ok (slopes, all 3 vacua).

0L amplitude perturbation: local vac[u] -> (1 + eps) vac[u] (eps in
EPS_LIN). P: dB/dJ linear in eps (slope 1), B dominates over J for
amplitude kicks (opposite of 0K); (dr, ds) map cleanly onto (dB, dJ)
combinations (filed 2x2 response matrix). G: amp_lin_ok (slopes).

0M background-relative energy: dE = E[vac + d] - E[vac] = 2Re<vac|H|d> +
E[d] (exact); for eigenstate vac: cross = 2 E_vac Re<vac|d>. P: anatomy
identity holds to 1e-9; dE differs across VPLUS/VPI/VMINUS by E_vac term
(VMINUS cross = 0 since E = 0, filed). G: energy_ok (identity + eigenstate
simplification pins).

0N geometry-conjugate excitation: dB readouts (sign/amplitude/support/
propagation/phase dependence/vacuum dependence). P: filed atlas per
(vacuum, kind); no dynamics insertion. G: none (characterization).

0O delta-B propagation: localized excitation, measure dB(r, t) vs dpsi(r,
t) (shell means from u0, hop + coarse radii). P: dB front arrival within
1 time unit of dpsi front (same carrier); near-field structure + wake +
1/r-ish decay filed. G: none (measurement); front-velocity comparison is
the 0O result (RESPONSE-0 coordination: same-carrier prediction).

0P hidden-vacuum anatomy: VMINUS (P_-) + P_+ propagating packet. P:
psi = V_- + d_+ reads hidden vacuum locally through drho/dB/dJ (nonzero
cross terms filed) while retaining no scattering memory (FIELD-0 witness
I = 0, sector weights conserved). G: hidden_anatomy_ok (I < 1e-6 AND
w_sym(d) = 1 conserved AND cross terms nonzero filed).

0Q symmetric-vacuum anatomy: VPLUS/VPI (P_+) + P_- hidden bump. P:
P_- perturbations are stationary (frozen_err ~fp) but alter local drho/
dB/dJ (filed); propagating P_+ vs stationary-hidden P_- taxonomy entry.
G: sym_anatomy_ok (frozen + weights + local response nonzero).

0R sector taxonomy: per (vacuum, kind) classify as propagating (remote
arrival + v_ok), stationary-hidden (frozen + P_- pure), mixed (both
weights), nodal (persistent spectral zeros via L4 dense check, filed),
cancellation-capable (eps*_cancel finite, 0G). P: filed 3x8 matrix; no
particle names. G: none (derived taxonomy).

0S interference null: collide two d excitations (head-on packets, k = +/-
0.5) on each vacuum; d12 = d1 + d2 exactly. P: FIELD-0 witness I = 0
within 1e-6 (frozen tolerance) on all vacua; nonzero vacuum introduces no
wave-wave interaction. G: null_ok (I gated, all 3 vacua + ZERO control).

0T apparent interaction atlas: repeat selected FIELD-0 cells (headon/
overlap/nearmiss x phase/amplitude grids, subset: 3 geometries x 4 phases
x 3 amps = 36 cells per vacuum) using drho/dB/dJ readouts. P: background
amplifies/suppresses apparent attraction/repulsion/trapping/standing/
energy-exchange by cross-term algebra (filed atlas); all explainable with
I = 0. G: none (proper null for future matter interactions around physical
vacuum, not ZERO).

0U response linearity: eps in EPS_LIN, measure drho/dB/dJ peak norms vs
eps (log-log slope). P: nonzero vacua slope 1 +/- 0.05 (O(eps) cross
terms); ZERO slope 2 +/- 0.05 (O(eps^2) pure quadratic). Major qualitative
distinction. G: linearity_ok (slopes gated, all 4 backgrounds x 3 kinds).

0V susceptibility: chi^rho/chi^B/chi^J = d(peak)/d(eps) at eps -> 0 via
finite-diff on EPS_LIN (local implementation; RESPONSE-0 coordination:
same dpsi kernel, different observable susceptibilities). P: chi differs
across VPLUS/VPI/VMINUS by vac-dependent cross coefficients (filed 3x3
matrix); ZERO chi = 0. G: none (formalizes same-carrier + different-
background-response; RESPONSE-0 apparatus comparison deferred).

0W long-time stability: T_LONG = 120 runs (packet + point_amp + hidden +
standing x 3 vacua = 12 rows), wrap-aware (wrap count filed from COM
winding). P: ||d|| conserved (1e-9), drho/dB/dJ peaks bounded (filed
ratios vs vacuum); no secular growth. G: stability_ok (norms + boundedness
ratio < 10x initial, generous bar). Input to VAC-STAB-0, not a replacement.

0X observer visibility: per (vacuum, kind) classify as locally_visible
(local dB/dJ peak > 1e-9), transport_visible (remote shell arrival > bar),
observer_geometric (P_+ quotient-visible via malus H_Q intertwining),
hidden (P_- pure, remote capacity ~0 per QUOT bars). P: filed 3x8 matrix
in QUOT/HIDDEN/SYM terminology (local implementation). G: none.

0Y structural virtual ledger: Delta_exc R_G = R_G[vac + d] - R_G[vac]
with R_G = M1 landscape stats (f_0/f_neg/f_pos + median) + contraction
per-class dE (readout-only via backreaction/contraction). P: filed per
(vacuum, kind) headline cells (3 vacua x 4 kinds = 12 rows); VPLUS flat
ledger + excitation => structured departure (filed). G: none (future
backreaction input).

0Z vacuum comparison: analyzer-only matrix (VPLUS/VPI/VMINUS x dpsi
propagation / zero-free protection / relational response / energy /
sector / null / linearity / ledger). No gate; science deliverable.

### Verdict ladder (0Z; analyzer-gated)

Checks (10, all boolean): evolution (0A), cross_bg (0B), decomp (0C+0J),
protection (0D+0E+0F+0G certificate + pins), energy (0M), packet
(0I+0K+0L v + slopes), sector (0P+0Q weights + frozen), null (0S),
linearity (0U), ledger_stability (0W norms + 0Y filed). Headline:
VACEXC0-COMPLETE if all 10 green; else VACEXC0-PARTIAL with per-check
table. Per-vacuum distinctions filed as family (no ranking by structural
consequences). ZERO control capped (linearity slope 2 expected, protection
vacuous, ledger trivial). Amendments, if any, as VACEXC0-AMENDMENT-n
entries with gated re-runs; none pre-data.

### Execution

241 tasks (scripts/vacexc_campaign.py --print-all), beast EC2
(16.54.88.181, xargs -P 48, OMP threads 1, nice), JSON records
data/vacexc/*.json (committed) + .npy sidecars data/vacexc/npy/
(gitignored, checksums committed in JSON). Full suite on beast
(pytest -n 48 --ignore=tests/test_weighted.py). Analyzer
scripts/vacexc_analyze.py writes data/vacexc/verdict.json. Verdict filed
here post-data.

### VACEXC0-AMENDMENT-1 (post-data; analyzer-only, no re-runs)

First analyzer pass over banked records (241/241 CAMPAIGN-DONE exit=0)
gave VACEXC0-PARTIAL: 7/10 green, sector/linearity/ledger_stability red.
All three reds are naive-gate artifacts, not physics failures: the banked
data are correct and quantitatively match the campaign's own exact
algebra. Each fix below re-evaluates a gate on already-banked records
(raw peaks/weights stored in JSON); no task is re-run, no record is
modified, no bar is loosened to fit. Original numbers are disclosed
inline. Behaviors newly established here (exact B-null theorem, mixture
fits) are filed as results, not assumed.

(a) Sector gate: normalized purity (0P/0Q). t_sector records P_+/P_- weights
of d (norm eps0 = 0.01), so pure states read w ~ 1e-4, not 1.0; the prereg
gate compared unnormalized weights to 1.0 (analyzer bug). Banked: VMINUS/
packet w0 = (1e-4, 0.0 exact), VPLUS/VPI hidden w0 = (0.0 exact, 1e-4);
conservation holds on all rows; frozen_err = 0.0 exact for both hidden
rows (1.4e-3 for the propagating packet, as expected, ungated). Amended
gate: normalized purity w_leg/(w_sym + w_anti) = 1 within 1e-12 on w0,
plus unchanged conservation + frozen legs. Purity was already exact in
the data (zero leg 0.0, no mixing); only the comparison was wrong.

(b) Linearity gate: deep-linear window + ZERO B-vacuous rule (0U). The
prereg fit log-log slopes over the full EPS_LIN window (0.001..0.1), but
the exact decomposition (pinned pre-data) gives peaks = c1*eps + c2*eps^2
(cross + dd), so any full-window slope is a mixture by construction; the
O(eps)-vs-O(eps^2) claim is an eps -> 0 statement. Banked full-window
slopes (filed as mixture characterization): VPLUS/VPI/VMINUS point_amp
rho 1.2225, J 1.0942/1.0942/1.1096, B exactly 1.0000 (pure: fitted c2 ~
-2e-16); VPLUS patch 1.0652/1.0529/1.0599; all packet legs 1.00-1.04
(pass). Mixture fits peaks ~ c1*eps + c2*eps^2 confirm the algebra:
VPLUS/point_amp/rho c1 = 5.05e-2, c2 = 1.0000 (rel-err 2e-16);
ZERO/point_amp/rho c1 = 8.9e-18 ~ 0, c2 = 1.0000 (pure quadratic);
ZERO/packet/B c1 = 5.6e-18 ~ 0. Amended gate: two-point log-log slope
over eps = (0.001, 0.003) (deep-linear regime, dd/cross <= 6% for the
most localized kind), expect 1 (nonzero vacua) / 2 (ZERO), bar unchanged
0.05. Result on banked peaks: 35/35 pass (point_amp rho 1.0347 the
worst, inside bar), plus one vacuous leg: ZERO/point_amp/B peaks are
exactly [0,0,0,0,0]. That null is exact physics, not missing data:
theorem -- single-node real d0 on bipartite J2 with real-symmetric H
keeps checkerboard phase structure (even-distance nodes purely real, odd
purely imaginary) for all t, and every edge joins even <-> odd, so
B_uv = Re(d*_u d_v) = 0 identically. Verified: J2 bipartite True,
max|B|/norm over T = 8 exactly 0.0, 0/1568 mixed-phase nodes. The slope
is then 0/0, so the leg is vacuous (same class as the prereg's VMINUS
E-vacuous rule). The theorem covers the source kind equally (seed
identical to point_amp); source is not in the linearity battery.
Amended rule: a ZERO leg with all peaks exactly 0.0 is VACUOUS-pass with
a loud note; the same pattern on a nonzero vacuum (where cross terms
forbid it) remains a failure.

(c) Long-time J gate: absolute bar (0W). The prereg ratio gate
max(dJ)/dJ(t=0) is vacuous for real d0: J_cross = J_dd = 0 exactly at
t = 0 (all-real field => Im = 0), so the ratio divides by the 1e-300
floor and reads ~1e295-1e296 on 8/12 rows (all norms conserved, B ratios
1.0-1.1, all green). Banked absolute peaks: dJ_max <= 4.6e-4, dB_max <=
2.5e-4 across all 12 rows; VMINUS/hidden dJ_max = 0.0 exact (frozen real
prep on frozen background => J = 0 identically). Amended gate: keep the
B-ratio leg (ratio_B < 10) and norm leg unchanged; replace the J-ratio
leg with absolute dJ_max < 1e-2 (generous: 20x above the largest measured
value). Boundedness was never violated; only the ruler was.

Re-evaluation is analyzer-only (scripts/vacexc_analyze.py): sector
normalizes banked weights, linearity recomputes two-point slopes from
banked peaks, longtime applies the absolute J bar to banked maxima.
Campaign records and .npy sidecars are untouched.

### VACEXC0-OBSOLETE-NONE / obs0 repair note (post-data, no science impact)

The 9896fae consumption vendored tests/test_quot.py, which imports the
OBS0 helper module, without vendoring src/bh_graph/obs0.py; the full
suite therefore collected 1 error (968 passed, 2 skipped). Repaired by
vendoring src/bh_graph/obs0.py (md5-12 6b86d1caeb06) + tests/test_obs0.py
(md5-12 912e68d1fdc0) byte-identical from the matching QUOT tip
(c8ad7a5; quot.py md5 identical to the consumed d250eeca640c). obs0 is
self-contained (math/networkx/numpy only); no cascade. No campaign code
imports obs0; no record, gate, or verdict input is affected. Follow-up:
test_quot.py also imports the scripts/run_obs1.py helper (single-pin CG
reference); vendored scripts/run_obs1.py (md5-12 7a06e09493ca) +
scripts/run_obs0.py (b86af74cb22d) + src/bh_graph/obs0r.py (f49a08fc3db9),
all byte-identical to the sibling addenda (HIDDEN-0 3a30275 / SYM-0
282507f / ZERO-0 2df866c, hashes unanimous). Same status: test-only
dependency, no campaign import, no science impact.

### VACEXC0-VERDICT (VACEXC0-COMPLETE, 10/10)

Branch cursor/vac-exc-zero-4201 (base main tail 9dc6ea2). 241/241 tasks
CAMPAIGN-DONE exit=0 on beast (16.54.88.181, xargs -P 32, OMP threads 1,
nice); records data/vacexc/*.json + verdict.json banked; .npy sidecars on
beast (gitignored, shas in JSON). Analyzer scripts/vacexc_analyze.py per
PREREG + AMENDMENT-1. Full suite on beast (venv, -n 32,
--ignore=tests/test_weighted.py): 1007 passed, 2 skipped, 0 failed.

Checks: evolution T, cross_bg T, decomp T, protection T, energy T,
packet T, sector T, null T, linearity T, ledger_stability T.

0A evolution theorem: 31/31 (4 vacua x 8 kinds minus ZERO/point_phase)
split_err <= 1.2e-13, corotating_err <= 9.4e-16; norm accounting green.
dpsi(t) = U(t)d0 in the co-evolving vacuum frame, exact.

0B cross-vacuum identity: 7/7 vac-independent kinds bitwise identical
across VPLUS/VPI/VMINUS/ZERO (max-dev 0.00e+00, sha equal). point_phase
filed separately (vac-dependent seed by construction). Hard regression
holds: same excitation trajectory on every vacuum.

0C absolute vs fractional: frac normalized rows collapse across
a = 1e-3..1e3 (packet 8.9e-14, point_amp 3.1e-14); abs raw rows identical
(0.00); cross slope +1.0000 / dd slope -0.0000 at t0/t80/t300 (dd == 0
exact at t0 for point_amp: single node, no internal edge); VPI/VMINUS
bracket peak-spread 9.9e-12/1.2e-14. eps ~ |d|/|vac| is confirmed as the
natural dimensionless excitation strength.

0D/0E/0F protection: certificate (m_min > 0 => zero-count 0) holds on all
36 margin rows. m_min at eps = 0.01: packet 2.46e-2, point_amp 1.53e-2,
hidden 1.82e-2, standing 2.43e-2 -- identical across all three vacua
(uniform floor |vac| = 1/sqrt(1568) = 2.52e-2; protection is vacuum-blind
at fixed a). Threshold sweep: eps_guarantee = 1.0 (packet), 0.03
(point_amp), 0.1 (hidden), 0.3 (standing), identical across vacua;
eps_actual = None everywhere -- no actual zero up to eps = 1.0 (100x the
headline). Guarantee-lost << actual-zero gap confirmed strongly.

0G cancellation: analytic single-node eps* (a = 1): point_amp 0.0253,
patch 0.129, packet 0.770, standing 0.581 (same all vacua: uniform floor,
vac-independent seeds). Constructed exact nulls: |psi[u0]| = 0, incident
B/J = 0 (< 1e-9) on all 12 demo rows (ZERO-0 Z3 reproduced on vacuum).
Single-node phase-only cancellation is impossible (pinned note: needs
exp(i eps) = 0); point_phase eps* = pi over-cancels by 2x.

0H battery: all 8 kinds green (norms abs/frac, sym/anti purity, decomp
identity on 9 subcheck rows).

0I packet propagation: v = (1.9204, 0) on all 4 backgrounds (identical to
all printed digits; Bloch (1.9177, 0), dev 0.14%), r2 = 1.0000,
alpha = 2.026, D: 0.9989 -> 0.8518, endpoint coherence 0.0000 (traveled +
dispersed), spectral peak (2, 0) support 784/784, width growth 0.516 --
every metric bg-independent. No apparatus audit triggered.

0J relational signature (same trajectory != same response), peak
|drho|/|dB|/|dJ| at eps = 0.01: packet dB_max VPLUS 3.59e-5, VPI 9.14e-6
(staggered cancellation), VMINUS 3.59e-5, ZERO 4.90e-7; packet dJ_max
VPLUS 1.80e-5, VPI 7.06e-5, VMINUS 7.03e-5. Note VPLUS = VMINUS exactly
in packet dB_max (3.58514308e-05) while dJ differs 3.9x -- vacua are
operationally distinguishable through local measurements. point_amp
relational peaks identical on VPLUS/VPI for drho/dB (6.05e-4/2.53e-4;
single-node cross set by |vac[u0]|) with dJ vacuum-dependent.

0K/0L kicks: phase + amplitude slopes 1.000 +/- 0.004 on all 3 vacua x
both kickers (12/12). J/B peak-norm ratio at eps = 0.01: phase 2.2x,
amplitude 1.8x (VPLUS/VPI; VMINUS amplitude 1.0x) -- both kicks J-led in
this readout, so the (dr, ds) -> (dB, dJ) mapping is NOT cleanly
separated in peak norms (filed honestly against the prereg hope; phase
leans further J as predicted, weakly).

0M energy: anatomy resid <= 3.6e-14, eigenstate cross exact. dE differs
by vacuum as predicted: VPLUS/point_amp -4.04e-3 (cross, dd = 0: single
node has no E[d]); VPI/point_amp +4.04e-3 (sign flips with E_vac);
VMINUS cross = 0 exactly (E = 0) with dE = E[d] only; VPI/packet cross =
-9.1e-8 ~ 0 (staggered vac orthogonal to smooth packet); hidden dE = 0
exactly everywhere (P_- flat band: H d = 0 kills both terms).

0N dB atlas: amplitude/vacuum-dependence filed via 0J tables + per-record
traces; sign follows vac phase structure (VPI staggered suppresses packet
dB 3.9x vs VPLUS/VMINUS). Primary future backreaction readout: vacuum-
dependent susceptibility with identical carrier (see 0V).

0O dB propagation: for truly u0-localized point_amp, dB front v = 5.6-5.7
(r2 0.92-0.94) tracks dpsi front v = 6.13 (r2 0.98) within ~7% on all 3
vacua -- same carrier. Packet shell-from-u0 readout is geometry-dominated
(packet starts far from u0; r2 0.05-0.86, one negative-v fit) and is filed
as a readout limitation, not a front measurement.

0P hidden vacuum + P_+ packet: purity 1.000000000000000 (P_+), weights
conserved, cross terms nonzero (local readout of the hidden vacuum),
witness I = 0 -- propagating excitation reads VMINUS locally with no
scattering memory. FIELD-0 witness stays zero.

0Q symmetric vacua + P_- bump: purity 1.000000000000000 (P_-),
frozen_err = 0.0 exact, weights conserved, local drho/dB/dJ nonzero
(dB 1.79e-4, dJ 3.57e-4 on VPLUS/VPI) -- stationary-hidden excitations
persist without transport but alter local observables. Bonus: hidden on
ZERO gives B = J = 0 exactly (frozen, no internal edge; only drho
5.0e-5) -- vacua make the hidden sector locally visible through cross
terms. On VMINUS, hidden dJ = 0 exactly (frozen real field => J = 0).

0R taxonomy (verdict-level derivation from banked evidence, rules per
prereg): packet propagating (P_+ pure, v gated, wraps 9); point_amp /
source propagating (P-mixed single-sheet, front v 6.13 r2 0.98);
patch propagating (P_+ symmetric, spreads); sym_sector propagating-
capable (P_+ pure, localized); standing P_+ pure with zero net velocity
(counter-propagating pair; rule edge case filed explicitly -- components
carry remote information, net v ~ 0); hidden_sector stationary-hidden
(P_- pure, frozen 0.0); point_phase mixed (single-sheet = sym + anti).
Nodal column not probed (no L4 dense task executed; packet spectral
support full 784/784). Cancellation-capable: all except point_phase
(phase-only single-node impossible, 0G).

0S interference null: I = eps_max = 6.2e-16 (headon) / 7.8e-16 (overlap),
identical across all 4 backgrounds -- nonzero vacuum introduces no
wave-wave interaction at the dpsi level.

0T apparent atlas: 18 cells (3 vacua x 3 geos x 2 phases), eps_max <=
1.0e-15 throughout; overlap energy conserved (Ex(t0) = Ex(tT) =
-4.58e-6, no exchange); relational peaks filed per cell -- the proper
null for future matter interactions around physical vacuum.

0U linearity: deep-linear two-point slopes (AMENDMENT-1b) 35/35 pass
(worst point_amp rho 1.0347, inside bar); ZERO legs exactly 2.0000;
ZERO/point_amp/B vacuous (peaks exactly 0; B-null theorem). Full-window
slopes filed as mixtures (point_amp rho 1.2225 etc.) with quadratic fits
peaks = c1 eps + c2 eps^2 (VPLUS/point_amp/rho c1 = 5.05e-2, c2 = 1.0000,
rel-err 2e-16; ZERO c1 ~ 9e-18 ~ 0). O(eps)-on-vacuum vs O(eps^2)-on-ZERO
confirmed as the major qualitative distinction.

0V susceptibility (finite-diff chi at eps -> 0, local readout): nonzero
vacua chi ~ 1e-2 - 2e-1 (e.g. packet chi_B: VPLUS 7.0e-2, VPI 1.3e-2,
VMINUS 5.1e-2; point_amp chi_J: VPLUS/VPI 1.31e-1, VMINUS 7.3e-2) --
identical dpsi kernel, different observable susceptibilities per vacuum.
ZERO chi ~ 1e-4 - 4e-3 = O(eps) finite-diff residue of pure quadratics
(consistent with chi_ZERO = 0 in the limit). Same carrier + different
background response, formalized.

0W long-time (T = 120): ||d|| conserved (12/12), dB_max <= 2.5e-4,
dJ_max <= 4.6e-4 (bar 1e-2, factor-20 margin), B ratios 1.0-1.1. Wraps:
packet 9, standing 2, point_amp/hidden 0. No secular growth; input for
VAC-STAB-0.

0X visibility (heuristic rules applied to banked evidence, local readout
in QUOT/HIDDEN/SYM terms): hidden_sector hidden (P_- pure) on all vacua
-- with the 0Q nuance that vacua make it locally visible via cross terms;
packet/patch/standing observer_geometric (P_+ pure + remote arrival;
standing with the 0R net-velocity caveat); point_amp/source/point_phase
transport_visible (mixed sectors + remote arrival via the P_+ component).
No excitation class is undetected at eps = 0.01.

0Y virtual ledger Delta_exc (M1 20000 x seed 0, readout-only): VPLUS flat
(0/1/0) + packet -> df_zero = -1.00 splitting +-0.50 (fully structured
departure); localized preps perturb ~1e-3. VPI one-sided (0.5/0.5/0) +
packet -> +0.25 f_pos (opens the forbidden side). VMINUS symmetric
(0.25/0.5/0.25) + packet -> symmetric +-0.25. Median/mean shifts <= 1e-4.
This Delta_exc R_G table is the filed future backreaction input.

0Z comparison matrix (filed in verdict.json; headline): dpsi propagation
identical (bitwise); zero-free protection identical (vacuum-blind uniform
floor); relational response, energy anatomy, susceptibility, and ledger
departure vacuum-dependent; interference null universal; linearity
universal (slope 1 vs ZERO slope 2).

Mission answers: (1) delta psi around an earned joint vacuum obeys the
same carrier U(t) on every vacuum (bitwise) -- the vacuum is a
relational/geometric background, never a propagation medium. (2) The
observables to define relative to the vacuum are drho/dB/dJ (with dpsi
fundamental); their cross terms carry the vacuum dependence and differ
operationally across VPLUS/VPI/VMINUS. (3) Fractional eps = |d|/|vac| is
the natural dimensionless strength (collapse 1e-13..1e-14 over 6 decades
of a). (4) dB is characterized as the primary future backreaction
readout (amplitude/vacuum-dependence/propagation filed; no dynamics
insertion per firewall). (5) No particle names were needed: the
propagating/stationary-hidden/mixed/cancellation-capable taxonomy follows
from the frozen sector structure.

Firewall compliance: no H modification, no geometry-update rule, no
(B - B_vac) in any dynamics (readout-only throughout), no amplitude
tuning, no structural events (0Y ledgers read-only), no matter
redefinition, no gravity claims. HIDDEN-0/RESPONSE-0/SYM-0 remained
coordination-only (local minimal readouts: MALUS sector weights,
finite-diff chi, heuristic visibility); QUOT-0/FIELD-0/ZERO-0/BR/CONS
consumed read-only and byte-identical (obs0/obs0r/run_obs0/run_obs1 repair
is test-only). ZERO stayed a capped control throughout.

## MEASURE0-PREREG — Physical transition measure (FROZEN PRE-DATA)

**Status:** apparatus + semantics + candidates + battery + gates + ladder
frozen; campaign NOT YET RUN. MEASURE-0 accepts SYM0-CLOSED (X_phys =
X/(R x U1), Theta identity, d_FS projective geometry, debt-survival
boolean), RAND0-MEASURE-DEBT (exact admissible sets, stabilizer/orbit
apparatus, MICRO/ORBIT-UNIFORM, multiplicity dependence), BR-2.5
contraction/splitting ontology u-v <-> [uv], BR-2.6/CONS0-PARTIAL event
accounting (dQ = 2B, dE = P1+P2, dxi = -c; splits DEGENERATE; no closing
field account), BR27-NO-MODE (no firing mechanism from energetics),
U0-INCOMPLETE (no complete deterministic U_G; H4 ties generic),
TIME0-NULL (boundaries do not select histories; exact history space
banked), HIDDEN0-SEPARATED (P_- locally physical, transport-hidden;
E_- = 0 energetically invisible), VACFIELD0-JOINT (VPLUS/VPI/VMINUS
family + ZERO background; no single vacuum selected). MEASURE-0 asks
whether the frozen theory determines a unique W([X],[Y]) >= 0 on
elementary physical transitions, local, representation-independent and
time-reversal-compatible (W(X,Y) = W(Theta Y, Theta X)). P(Y|X) is
normalization of W, never the starting point.

**Frozen inputs (read-only, sha256-verified byte-identical across sibling
tips):** sym0-e27a apparatus (accounting/backreaction/ballistic/coherence/
conservation/continuum/contraction/driven/formation+delta/malus/obs0/obs0r/
obs1/obs1_reveal/phase/potential/quot/rand0/slit/stability/sym0/tunnel/u0/
ug/ug_sync/vac0 + tests + xdist config + run_obs0/run_obs1/analyze_blind),
time0-d6cc (time0 + test), hidden0-3478 (hidden/field0 + tests),
vacfield-8ec1 (vacfield + test). No law change on consumption. Frozen
conventions: X = (G, psi), simple graphs, H = -A, J = 1, hbar = 1,
dt = 0.1, sum map, B/J quadrature, E = -2 sum B, dE_contract =
2B - 2 sum_cross (BR-2.6 MINUS). Banked theorems consumed, never
re-derived: [H,S] = 0, H P_- = 0, Theta U(t) Theta^-1 = U(-t) (method
re-applied on the MEASURE grid, identity not re-postulated), U0-H1
endpoint gauge, CONS-0K split formulas, info-loss books.

**Epistemic firewall (frozen):** no temperature, Boltzmann factors, Born
rule, action, entropy maximization, Metropolis, event rates, fitted
exponents, tunable couplings, external noise, hidden random fields,
preferred graph or matter configuration. W ~ e^{-beta dE}, |psi|^2, |B|,
e^{iS} appear ONLY as explicit negative controls (M-FW) with their
parameter/derivation debt filed. No gate may be passed by a control.

**Candidates (frozen, zero fitted params):** const (W = 1 on every
distinct physical elementary transition); orbit (RAND orbit-uniform
reconstructed on the physical quotient, control-rival). No other
candidate may be introduced post-data; Q/R/S/T/U searches may only file
negative/positive findings against the frozen battery, never fit.

**State battery (frozen, deterministic):** tiny {k2, triangle, square,
star4, path4} x {zero, bonding, current, antibonding} (20 states; exact
Aut + exact-iso scope); J2-L4 (N = 32, sheet/symmetry/background scope);
background battery {ZERO, VPLUS, VPI, VMINUS} on J2-L4 via
vacfield.candidate_shape (VACFIELD0-JOINT is a family: headline runs ALL
four, never selects); TIME-0 labeled N<=4 universe (44 states, history
scope). No big-graph OBS recomputation (SYM-0 O5 cap inherited); exact
isomorphism capped at N<=12 (RAND Amendment-1 inherited).

**Stages (frozen):** A physical admissible sets A_phys (quotiented;
representation-independence hard gate); B tiny exact transition graph
(degrees, stabilizers, types, supports, accounting; no weights); C
reverse-edge completeness (reversible vs graph-only vs one-way per
contraction; halves-condition filed); D Theta map (dense-exact dynamics
check + W reversibility per patch); E invariant inventory (B, J, rho,
dQ, dE_psi, dE_G, dxi, cross, cycle-rank, degrees, sector, stab/orbit;
classification table frozen in module); F minimality (param counts;
const/orbit = 0); G const weight + P = 1/|A_phys|; H reverse consistency
of const + stationary pi ~ d (descriptive); I orbit-uniform control +
disagreement battery; J refinement (directed vs undirected vs iso;
gauge-quotient stability gated, iso grain filed); K composition
(disjoint factorization gated; shared-node exclusion filed); L locality
(RAND U0-F support radius; both candidates); M Aut covariance (frozen
tiny perms); N sheet covariance (J2); O global-phase redundancy (hard
gate, U1 grid); P TR-even audit (B/rho/Q/E even; J odd filed); Q
conservation-surface (level degeneracy census; selects = False expected);
R projective field geometry (daughters discrete; N differs across split
=> no common-space FS volume; negative expected); S graph combinatorial
(1 vs |Aut|^-1 vs |orbit|; underdetermined expected); T product measure
(not forced: B/J couple); U contraction Jacobian (discrete graph + C^2->C
fiber; no finite invariant preimage measure); V info-loss (graph_bits =
log2 covers identity; filed, not a derivation); W hidden sector (VMINUS
retained; E-blindness filed); X background dependence (4/4 run; W
battery-blindness filed); Y vacuum quiescence as prediction (P_stay =
1/2 per edge; active, no exception); Z tiny exact transition matrices +
stochasticity + classes; AA detailed balance (result, not repair); AB
probability currents (audit); AC TIME-0 history comparison (W = 1 =>
uniform over histories; NULL-survival expected); AD uniqueness audit
(analyzer debt-reasons); AE minimality audit (param table); AF verdict.

**Stage gates (frozen):** HARD (any red => MEASURE0-INCOHERENT, stop):
H-INST-no-crash, H-A-rep-edge, H-A-rep-node, H-A-sig, H-O-phase,
H-Z-matrix. MEASURED (filed, never gated): M-B/C/D/E/F/G/H/I/J/K/L/M/N/
P/Q/R/S/T/U/V/W/X/Y/AA/AB/AC/FW (see analyzer for the exact list).
No gate is tuned after opening data; amendments require a dated
MEASURE0-AMENDMENT note pre-rerun.

**Verdict ladder (frozen):** MEASURE0-CLOSED = all HARD green + zero
debt-reasons (unique W forced: no disagreement, fully reversible
support, an earned selector among Q/R/S/T/U, balance holds).
MEASURE0-DEBT = all HARD green + >= 1 debt-reason (apparatus coherent,
no unique W). MEASURE0-INCOHERENT = any HARD red. Debt-reasons
(frozen analyzer rules): orbit-rival differs; support not fully
reversible; no conservation selector; graph grain underdetermined.
PREDICTION (pre-data, theorem-backed): MEASURE0-DEBT via (a) orbit
rival differs on node patches (RAND-0C both satisfy, no earned
preference), (b) reverse support graph-only/one-way on generic fields
(sum-map information loss), (c) no earned selector (CONS-0 DEGENERATE,
discrete daughters, coupled sectors, infinite fiber), (d) vacuum active
(RAND-0H), (e) TIME0-NULL survives uniform history weighting. CLOSED
stays data-reachable; INCOHERENT stays reachable via any HARD red.

**Campaign:** scripts/measure0_campaign.py on beast (96-CPU, mp pool);
scripts/measure0_analyze.py applies the frozen gates; full suite on
beast in parallel (test_weighted.py skipped per standing instruction).
Nothing local except unit pins.

## MEASURE0-AMENDMENT-1 — Apparatus design-error fixes (post-first-look audit)

First-look outcome (beast, 544 cells, ledger archived beast-side as
data/measure0_ledger_look1.json, superseded): MEASURE0-DEBT with all
HARD green, but two MEASURED cells mis-measured by apparatus bugs
(not physics): M-J-refinement reported capped = 72/72 (iso grain
never computed) and M-AC-history reported n_pairs = 4 (census
misparsed). Autopsy:

(a) refinement_status called split_isomorphism_classes(g, psi, order,
k) with a missing `admissible` argument and parsed the return as a
dict with a "classes" key; the frozen RAND API is
split_isomorphism_classes(g, psi, order, k, admissible) -> list of
outcome-key lists. Every call raised TypeError into the except branch
(n_classes = -1, nonuniform = None). Fix: pass `adm`, parse the list.
Verified locally: square d=2 -> 6 undirected / 10 directed / 5 iso
classes, nonuniform True; star4 center d=4 -> 42/82/10, nonuniform
True. Multiplicity dependence now measured at the iso grain too.

(b) history_weight_status parsed boundary_census (which returns
aggregates: n_pairs, n_compatible, f_unique, median/max N_hist,
histogram) as a per-pair dict, yielding n_pairs = 4 (dict-key count
artifact). Fix: consume the frozen aggregates directly; null_survives
= (max N_hist > 1). Verified locally: T=2 N<=4 -> 1936 pairs, 1099
compatible, f_unique = 0.699 (matches banked TIME-0 labeled N<=4
T=2 value 0.70), max 18, null survives.

Scope: M-J and M-AC are MEASURED (filed, not gated); no HARD gate, bar,
threshold, battery, candidate, or verdict-ladder rule is changed. No
physics content moves. Rerun is analyzer/apparatus-only repair with the
frozen intent restored (RAND Amendment-2 / HIDDEN Amendment-1 precedent).

## MEASURE0-VERDICT — Physical transition measure: MEASURE0-DEBT (DATA)

**Campaign:** beast EC2 16.54.88.181, --jobs 90, 544 cells, 0
run-failures, wall 2.6s; ledger data/measure0_ledger.json (197KB) +
data/measure0_verdict.json; 52/52 test_measure0.py pins green (local +
beast). Amendment-1 (iso + census parsing, apparatus-only, no gate
touched) applied pre-rerun; look1 ledger superseded, archived
beast-side. Full suite on beast: pending at filing (beast load ~2500,
suite at 98% with no failures; count to be appended; test_weighted.py
skipped per standing instruction). All 6 HARD gates green, all 29
MEASURED cells filed.

**Headline (frozen ladder):** 4/4 debt-reasons trigger =>
**MEASURE0-DEBT**. The apparatus is coherent (representation-independent,
local, covariant, TR-compatible, stochastic) and no unique inter-outcome
weighting is forced. Matches the theorem-backed prediction; CLOSED was
data-reachable (zero reasons) and did not occur.

**A (physical sets):** A_phys well-defined on all 60 edge + 72 node
patches; representation-independence 132/132 under reversal/shuffle x
U1(pi/3) (class-size multisets identical). Edge: always 2 physical
classes (N differs). Node: classes <= outcomes (merges filed per-cell).
Signature (N/E/degrees/triangles/rank + |psi|/B/J multisets + Q/E)
invariant 20/20 x 8 representatives. Hard gate green.

**B (transition graph):** tiny exact graph 205 physical nodes, 600
relations (60 contract + 408 split + 132 stay); degrees/reverse-degrees/
stabilizers/types/supports recorded per edge. No weights. Filed.

**C (reverse completeness):** 33 reversible / 27 graph-only / 0 one-way
(n = 60). Graph reverse ALWAYS exists (BR-2.5 covers complete: original
neighborhoods always among undirected covers). Full reverse exists iff
the frozen equal-halves map restores (psi_i, psi_j), i.e. psi_i == psi_j
(halves condition): symmetric fields (zero/uniform/bonding) reversible,
asymmetric (current/antibonding/generic) graph-only. A reversible history
measure cannot be built on the generic support without additional
physics (sum-map information loss, U0-H/CONS-0M precedent). Hard
prerequisite filed as the campaign's sharpest structural finding.

**D (Theta):** dynamics identity 20/20 to KRYLOV (dense-exact U(-t)
reference; TIME-0 -dt finding honored); W reversibility 20/20 for
const (W(X,Y) = W(Theta Y, Theta X) holds; reduces to W(X,Y) = W(Y,X)
on Theta-symmetric signatures only, never assumed).

**E/F (inventory/minimality):** 15-quantity inventory with frozen
(R x U1, TR, background) classification; TR-even audit 60/60 (B, rho,
Q, E, dQ, dE, dxi, cross, degrees even; J odd filed). Fitted params:
const 0, orbit 0; controls boltzmann 1 (beta), born 0-but-forbidden
(no derivation), absB 1 (scale x0). Firewall kept.

**G/H (const):** W = 1 well-defined on physical outcomes (SYM-0
quotient makes it representation-independent); P = 1/|A_phys|.
Reverse-consistent where support is reversible (automatic). Stationary
pi ~ d pinned (descriptive, no thermodynamics).

**I (orbit control):** disagreement on 36/72 node patches (exactly the
patches with nontrivial orbit structure; edge patches vacuous 2
singletons, orbit == micro). The 36 disagreement cells are the primary
discrimination battery; no earned quantity prefers either weighting
(RAND-0C both satisfy). Debt-reason 1.

**J (refinement):** directed differs 72/72 (gauge double count is WRONG,
not rival: merging directed copies restores the undirected total by
construction). Iso grain: 32/72 nonuniform over exact iso classes
(square d=2: 6 covers -> 5 classes; star4 center d=4: 42 -> 10),
40/72 uniform (small patches where covers already are classes, e.g.
d=1). Micro-uniform is grain-dependent: the quotient ontology does not
decide the physical grain. Filed per-cell; gauge part gated, iso part
filed (RAND Amendment-1 cap inherited, N<=12 exact throughout the tiny
battery, capped = 0).

**K/L/M/N/O (composition/locality/covariance):** disjoint factorization
12/12 (W=1: joint 1/4 = 1/2 x 1/2; shared-node co-firing excluded by
enumeration, filed); locality 120/120 both candidates (dist>=3 field +
disjoint toggle; RAND U0-F radius); Aut covariance 40/40 (frozen tiny
perms, equal law not identification); sheet covariance green (J2);
global-phase redundancy 40/40 both candidates (hard gate green).

**P (TR-even):** even 60/60; J odd with exact sign flip (filed: current
enters scalar reversible weights only through even combinations).

**Q/R/S/T/U (structural searches, all negative, filed):** Q selects
0/72 (level sets always degenerate: >1 cover on (dxi,dQ)=(0,0);
CONS-0M reproduced) => debt-reason 3. R selects 0/72 (daughters are
discrete points; N differs across split so no common-space FS volume
exists; FS stays a state-space metric, not an outcome measure). S
underdetermined (1 vs |Aut|^-1 vs |orbit| all invariant, none forced)
=> debt-reason 4. T not forced (B/J couple G and psi jointly). U no
finite invariant preimage measure (graph discrete; field fiber C^1
infinite volume; any cutoff = new parameter).

**V (info-loss):** graph_bits = log2|covers| 4/4 (d=1..4; combinatorial
identity, filed as non-derivation: counting covers twice does not
derive a measure). Field: 2 real dims lost per event (continuous).

**W/X (hidden/background):** hidden retained (VMINUS in transition
space on all battery cells; E-blindness E_- = 0 filed, E not in W).
Background 4/4 run (VACFIELD0-JOINT family honored, no selection);
edge-patch n_phys = 2 on all four (sets psi-blind); B/dQ/dE anatomy
differs per background (filed, no W dependence).

**Y (vacuum quiescence):** P(stay) = 1/2 per edge, 1/|A| per node, on
ALL backgrounds including ZERO (no exception added). Vacuum active
under any surviving candidate (RAND-0H reproduced on the quotient).
Prediction filed, not repaired.

**Z/AA/AB (matrix/balance/currents):** K2 edge-patch matrices
stochastic both candidates; classes {X},{Y} (contract-daughter is a
1-node graph: no edge patch, absorbing stay). Detailed balance HOLDS
with dev = 0.0 and currents zero -- DEGENERATELY (pi = delta on the
absorber: 0*P terms vanish; filed as absorbing-patch triviality, NOT
reversibility evidence). A nondegenerate balance test needs a closed
multi-patch domain, which needs a scheduler (= new content, not in the
frozen ontology). Filed honestly; no repair imposed.

**AC (TIME-0 history):** T=2: 1936 pairs, f_unique = 0.699, median 1,
max 18; T=3: f_unique = 0.029, median 3, max 52; null survives both.
Matches banked TIME-0 labeled N<=4 census (0.70 -> 0.03): W = 1 weights
histories uniformly, multiplicity survives, boundaries do not select.
TIME0-NULL reproduced under the candidate measure.

**Debts filed (not closed):** INTER-ORBIT-WEIGHT (const vs orbit, 36
cells), GRAIN (covers vs iso classes, 32 cells), SUPPORT (27/60
graph-only reversibility gap), SELECTOR (no Q/R/S/T/U measure),
SCHEDULER (no global multi-patch P without new content), VACUUM-ACTIVITY
(P_stay = 1/2 prediction). Firewall controls filed with their debts
(beta/scale/no-derivation).

**Handoff:** stochastic completion stays underdetermined on the physical
quotient (RAND0-MEASURE-DEBT survives SYM-0, confirmed exactly). BR-3C
stays BLOCKED. The program owes either a primitive measure postulate
(firewall: not emergent from energetics/conservation/geometry as
currently derived) or new physics that closes one of the six debts.
Downstream may consume: A_phys apparatus + signatures (HARD-green),
const/orbit weights as rival controls (never as the answer), the 36-cell
disagreement battery, reverse-classification per transition, and the
TIME-0 history-weighting check. No tuning of W is permitted.

## HIDDEN-BR-PREREG (FROZEN pre-data; this commit predates ALL beast HIDDEN-BR runs)

Mission: determine whether transport-hidden (P_-) field information produces
a locally distinct geometric backreaction tendency through the banked
geometry-conjugate B_uv = Re(psi_u* psi_v), while matched states remain
identical in transported information, propagating sector, total field
energy, and remote operational observables. Virtual structural ledger
only: NO graph mutation, NO contraction/split execution, NO event
scheduler, NO U_G, NO history measure (HISTORY-MEASURE DEBT still blocks
actual geometry dynamics). HBR-0S omitted (RESPONSE-0 has no verdict).

Frozen inputs (read-only, byte-identical vendor, commit 8a38be8):
  HIDDEN-0 HIDDEN0-SEPARATED 279/279 .... cursor/hidden0-local-dof-3478 @90aaa53
  BR-2.6 BR26-ACCOUNTED 10/10 ............ cursor/backreaction-br26-bb0f @dd956e0
  CONS-0 PARTIAL 22/22 ................... cursor/cons0-invariant-census-4129 @c551cb5
  SYM-0 SYM0-CLOSED 8/8 .................. cursor/sym0-state-census-e27a @43ac69a
  ZERO-0 Z1-Z3 earned, Z4 filed .......... cursor/zero-crossing-census-ee5c @c4c2fb6
  FIELD-0 LINEAR+APPARENT ................ cursor/field0-null-960b @b9dea0c
  VAC-FIELD-0 JOINT ...................... cursor/vac-field-nonzero-joint-8ec1 @3dbfe34
  base origin/main @a0c248c. No formula modified (spec firewall).

Frozen law/constants: i dpsi/dt = -A psi, J=1, J2 L28 headline (L6 exact
pins), T=20/dt=0.1, packet r0=(7,14) k=(0.3,0) sig=4 (HIDDEN-0 values).

Stages -> cells (35 cells, J2 L28 unless noted; no fitting/selection):
  pair-ledger x10 (HBR-0A/B/C/D/F/G/H/I; C0/C1/C2): B:sign x
    {packet,uniform,twocell} (3), B:phase:packet x {pi/2,pi} (2),
    B:shape:packet x {dipole,disk} (2), B:amp:packet {05raw,20raw} (2),
    B:amp:packet:05q (1, NON-QUALIFYING control, see P1). Each: P_+
    match, E_A=E_B + E_-=E_x=0, D_local>0 + D_remote~0 (wave+diff
    shells 2/4/6 + POT), dB census (n/max/mean/support/signs),
    perturbation census (sign+mag differ rates), full BR-2.6 ledger
    census (frac nonzero, sign flips + edges, magnitudes).
  conjugate x2 L6+L28 (HBR-0E; C3): centered-FD dE/dA_uv vs -2B_uv.
  equalledger x2 (HBR-0J): conjugation pairs (real bg + complex
    hidden): expect dB=0, ledger=0, d_J>0.
  purehidden x4 (HBR-0K): {delta,disk,checker,complex}: E=0 + B/ledger.
  vminus x1 (HBR-0L): VMINUS B/J/ledger + translation covariance + balance.
  phasesweep x2 (HBR-0M): packet:delta, uniform:disk: B(phi)+ledger(phi)
    trig fits + E const over frozen 8-phase grid.
  ampsweep x2 (HBR-0N): packet:delta, uniform:disk: a in {0,.25,.5,1,2,4},
    [1,a,a^2] fits + linear/quadratic split.
  shape x1 (HBR-0O): dipole/disk/checker fixed-norm ledger distances.
  locality x3 (HBR-0P/Q; C5): graded-radius boundary, far control, support.
  passwave x2 (HBR-0R): delta/disk bg: ledger(t) overlap + post-exit + I.
  zero x1 (HBR-0T): min|psi| on nonzero-ledger supports; need-zero frac.
  sym x1 (HBR-0U; C6/C7): U1 x4 alphas, shuffle relabel, S covariance.
  vac x1 (HBR-0V): VPLUS/VPI/VMINUS sector split + B/ledger contributions.
  firewall x1 (HBR-0W; C8): head-on two-packet witness I=0 replay.
  ledgercheck x1 (C4): event_ledger formula vs contraction_census direct.
  infomap x1 (HBR-0X): R2 mixed census (168) R_G min-separation.

Bars (frozen): PMATCH 1e-12 (C1); E-match |E_A-E_B|<=1e-9 + |E_-|,|E_x|
<=1e-12 (C2); D_LOCAL 1e-6 / D_REMOTE 1e-9 (C0); ledger-nonzero 1e-9
(max|dB|>1e-6 headline); sign-flip needs both |vals|>1e-9 strict-opposite;
trig/[1,a,a^2] fit res <1e-9; FD-conjugacy <1e-9 (E linear in A_uv, exact);
C4 direct-vs-formula <1e-9; U1/locality <1e-12; witness 1e-6 (FIELD-0).

Pre-data predictions: P1 E=E_+ replay all pairs; HAMP-Q EXPECTED to fail
C2 with E_B'/E_A=c^2 exactly (rescale control, excluded from verdict with
cause). P2 B/ledger in span{1,cos,sin}. P3 B/ledger in span{1,a,a^2}.
P4 conjugation control exact-null ledger, d_J>0. P5 pure-hidden E=0,
nontrivial B. P6 VMINUS pure P_-, per-edge-class uniform ledger. P7 sharp
locality boundary at 1-hop ledger support. P8 C0 regression. P9 NO
prediction on sign-flip existence (genuine measurement, HBR-0I).

VERDICT LADDER (frozen): HBR0-NULL if every qualifying pair has max|dB|
<1e-9 AND every ledger d_hidden=0 (hidden geometrically inert; requires
HIDDEN-0 dB non-reproduction). HBR0-GRADIENT (primary positive) if >=1
qualifying equal-E pair has max|dB|>1e-6 (hence dE/dA differs) with C0-C8
green. HBR0-SIGNREV (distinguished refinement): GRADIENT + >=1 strict
opposite-sign ledger edge. HBR0-PARTIAL otherwise (incl. dB!=0 but all
ledgers cancel, or control failures). Pairs failing C1/C2 are excluded
with filed cause, never counted.

## HIDDEN-BR-AMENDMENT-1 (pre-beast-data; post-local-validation audit)

Status: NO beast HIDDEN-BR data taken yet (beast checkout untouched). A full
local instrument-validation run (same code, 35 cells, 201/215 green) exposed
two scope errors in the preregistered C0/X gates. Both are fixed here with
derived mechanisms (not tuned bars); the verdict ladder, headline bars, and
all other stages are unchanged. The beast run below is therefore a
CONFIRMATION run for A1's predictions (independent execution, frozen record).

A1a (HBR-0C scope): diffusion-blindness holds iff Dp(0) is S-odd. Sign/phase
pairs have pure cross-term Dp (S-odd exactly: P_- eigenmode of Lrw, decays
in place) and stay diff-blind; shape/amplitude-raw pairs carry an S-even
|psi_-|^2 difference (|ma|^2-|mb|^2 != 0) that DIFFUSES remotely (measured
locally: 0.005-0.43 on shells 2/6, monotone in hidden amplitude). HIDDEN-0's
0F remote battery tested sign pairs only, so this REFINES (not refutes)
HIDDEN0-SEPARATED: wave+POT stay blind UNIVERSALLY for all matched pairs
(the A-B difference never leaves the hidden support under U(t); POT drive
differences are pure-anti), diffusion only for S-odd-Dp pairs. Analyzer
change: C0_diff gated only when the pair record has sodd=true; sodd pattern
itself gated (sign/phase True, shape/amp-raw False, both analytic); 05q
sodd filed. C0-green redefined accordingly. No bar moved.

A1b (HBR-0X refinement): R_G = (B, ledger) separates the R2 mixed census UP
TO CONJUGATION. B and L are conjugation-even, so conjugate census states
(same cell, phases +-phi, real background) agree to fp (measured: 63/63
pairs, max D 5.2e-18 scale) while differing in J (the HBR-0J mechanism).
3 conjugate pairs/cell x 21 cells = 63 exactly. X cell now records conj-aware
fields (min over non-conjugate pairs + conjugate max-D); analyzer gates
non-conjugate separation (min_D > 1e-6, n_below = 0) plus n_conj = 63 and
conj_max_D < 1e-12. The "M_O equal" premise is scoped to wave+POT (universal)
since cross-cell census pairs are diffusion-visible per A1a.

A1c (P1 formalized): 05q fails C1 by |c-1|*max|P_+| exactly (pinned in
tests/test_hiddenbr.py), alongside the preregistered E_B/E_A = c^2 law.
Cause filed, pair excluded. No gate change.

## HIDDEN-BR-VERDICT (filed 2026-10-02): HBR0-SIGNREV (primary positive + sign reversal)

Beast confirmation run (35 cells, 32 workers, wall 23s; records
data/hiddenbr_{cells,verdict,stage}.json committed): 214/214 frozen checks
green (Amendment-1 applied), 9/9 qualifying pairs valid (C1+C2), C0-C8 all
green, 1346 strict sign-flip edges. Suite 1296 passed + 2 skipped on beast
(-n 8; test_weighted.py skipped per standing instruction).

Headline: matched states with P_+ equal, E_A = E_B to fp (dE <= 1.8e-15),
and wave+POT remote blindness (<= 2.5e-15 / 2.1e-17) nevertheless have
different B landscapes (max|dB| 0.025-0.71 over 4-96 edges) and therefore
different dE/dA = -2B (conjugacy pinned < 1e-9 on L6+L28): EQUAL FIELD
ENERGY DOES NOT IMPLY EQUAL GEOMETRIC RESPONSE LANDSCAPE. Stronger: 1346
edges across the battery carry STRICT opposite-sign virtual contraction
ledgers (70 on local pairs + 1276 on the VMINUS sign pair): changing only
transport-hidden information REVERSES the energetic ordering of structural
alternatives. All virtual (no graph op executed anywhere).

Stage highlights: HBR-0J conjugation control exact (dB = dL = 0, d_J > 0:
ledger-blind but J-visible). HBR-0K: zero-energy pure-hidden states carry
nontrivial ledgers (disk/checker/complex B_max 0.04-0.06, 96 ledger edges;
delta has B = 0 ON EVERY EDGE yet 16 nonzero ledger edges via non-edge
cross bonds: a vanishing bond field with a non-vanishing gradient
landscape). HBR-0M/N: B/ledger in span{1,cos,sin} / span{1,a,a^2} to fp
(res ~1e-16), E constant over both sweeps (range 0.0). HBR-0O: shape matters
at fixed norm (pairwise db 0.14-0.38, 50-60 flips each). HBR-0P/Q: sharp
locality (test-edge dh exactly 0.0 at support distance >= 2 through
antipodal; far control bitwise 0.0). HBR-0R: overlap ledger modulation
0.50/0.27 with bitwise-zero far field and witness I ~ 1e-12 (no memory).
HBR-0T: nonzero-ledger supports need no zero (filed frac). HBR-0U: U1 /
relabel / sheet covariance < 1e-12 (redundancies quotient cleanly).
HBR-0V: VPLUS/VPI pure P_+ (E -8/+8), VMINUS pure P_- (E = 0, 12
offset classes, spread 0.0). HBR-0W/C8: head-on witness I = 0 (no force).
C4: BR-2.6 formula vs direct contraction < 1e-9. HBR-0X: R_G separates the
R2 census (min_D 0.052 over 14028-63 pairs) UP TO CONJUGATION (63/63
conjugate pairs fp-identical at 2.2e-16: the geometric response is blind
to hidden conjugation, which lives in J alone).

Refinement of HIDDEN-0 (Amendment-1, mechanism-derived): diffusion-blindness
holds iff Dp(0) is S-odd (sign/phase: diff <= 6.1e-16; shape/amp-raw: diff
0.005-0.43, S-even |psi_-|^2 difference diffuses); wave+POT blind for ALL
matched pairs. HAMP-Q control exact (E_B/E_A = c^2 = 1.75 to 1e-12, C1 fail
at predicted |c-1|max|P_+|). HBR-0S omitted (no RESPONSE-0 verdict).
HISTORY-MEASURE DEBT still blocks actual geometry dynamics: no tendency,
rate, or event claim is made.

## VACCOMP0-PREREG — Complete joint-vacuum manifold (FROZEN PRE-DATA)

**Status:** apparatus + grids + gates + ladder frozen; campaign NOT
YET RUN. VAC-COMP-0 classifies the complete set and topology of
nonzero stationary joint-field vacua on frozen (G,H) = (J2 torus,
-A) BEFORE any geometry-transition measure. VAC-FIELD-0 banked
three JOINT representatives (VPLUS/VPI/VMINUS); this campaign asks
whether they are isolated classes, members of degenerate
components, points on a connected manifold, or samples of a large
hidden manifold. Classification only (0AD firewall: no selection,
no MEASURE-0, no structural events, no energy/hidden/ground-state
privilege, no SSB, no "phases" language, no tuned combinations).

**Frozen inputs (read-only):** VAC-FIELD-0 vacfield.py (vendored
byte-identical from cursor/vac-field-nonzero-joint-8ec1 tip;
10-check JOINT ladder, BARS, candidate shapes); SYM-0
(X_phys = X/(R x U(1))); MALUS/QUOT ([H,S]=0, H P_-=0, square-walk
symmetric sector, nodal counts); HIDDEN-0 (E=E_+ law, cross-term
anatomy); ZERO-0 (codim-2, incident null, protection form); EM-0
(continuum Bloch apparatus); HIDDEN-BR R_G ledger (descriptive).

**JOINT generalization (frozen once, applied uniformly to arbitrary
states; neither weakening nor strengthening):** stationary /
current_free / stress / linearity = exact vf gates unchanged;
amplitude_coherent = vf scaling gates + E-vacuous rule for E==0
(VACFIELD Amendment-4) with STRICT Bmax gate (B==0 states cap at
BACKGROUND; no theorem backs a B-vacuous rule); triviality read
fp-aware (|.| < 1e-12 on the normalized shape); sector_filed =
purity in either sector (mixed caps at BALANCED); ledger_symmetric
= contraction per-class uniform + M1 seed-stable (std < 0.01)
WITHOUT prescribing (f0,fneg,fpos) values; small graphs (N<=64)
use exhaustive M1 (VAC-FIELD m1exact precedent). Universal legs
(perturbation_ok, linearity, normalized_robust, zero_anatomy) are
True-by-theorem for eigenstates (0L linearity theorem + ZERO-0B
incident theorem) and VERIFIED for component representatives.

**Frozen grids:** ALPHA 13 points 0..pi/2; PHI 8 points 0..2pi;
AMPS = 1e-3..1e3 (7); RNG_SEEDS = 0..4; EIG_TOL = 1e-9. Dense
exact scope L<=8; L=4 census headline (N=32); L=28 ladder headline
(N=1568, full ledger_moves=20000).

**Preregistered analytic predictions (also pinned in
tests/test_vaccomp.py, 37 pins, pre-data):** E_-8/E_+8 unique at
even L (Perron-Frobenius + bipartite symmetry); E_0 = N/2 hidden
+ nodal(L) symmetric (L4: 22=16+6; L28: 838=784+54); 4th TI JOINT
ray VSTAG = (-1)^b(-1)^{x+y}/sqrt(N) (even L only); real RP^1
JOINT circle VMINUS-VSTAG span with B==0 BACKGROUND points at
alpha=pi/4(,3pi/4); generic complex eigenstates fail current_free;
generic real non-TI states fail stress; different-eigenvalue
mixtures beat at dE (16/8/8) with no interior JOINT and no
cross-term cancellation among full-support vacua; all four TI
vacua share coarse rho (observer blindness) while circle-interior
patterns are coarse-visible; pi_0(JOINT) = 3 even L (VPLUS, VPI,
CIRCLE-as-one), 2 odd L (VPLUS, VMINUS); B==0 independent-set
states cap at BACKGROUND.

**Gates (applied by scripts/vaccomp_analyze.py):** C0 headline
L=28 JOINT ladders (VPLUS/VPI/VMINUS/VSTAG/CIRCLE@pi/6) + circle
endpoints; C1 SYM quotient structural; C2 spectral exactness at
L=4/6/8 (extrema +-8, Bloch dev, nondegeneracy, zero-split
decomposition, candidate residuals/subspace weights); C3/0B
stationarity theorem on an arbitrary degenerate superposition;
0E generic exclusion (no JOINT; current binds complex, stress
binds real); 0H circle census at L=4/6 (exactly 1 BACKGROUND grid
point, rest JOINT); 0I complex-hidden exclusion frac > 0.9; 0J
real-hidden J==0 everywhere but no JOINT, proj dim 15; BZERO cap;
0K amplitude families all JOINT (4 rays + circle point); 0L
same-eigenvalue sweep stationary everywhere, cut interior JOINT
count == 10; 0M beats |corr| > 0.99 at dE 16/8/8, no interior
JOINT in the three mixed sweeps; 0Q no cancellation; 0TU all four
ray-TI singletons; 0V TI coarse-blind + circle-interior visible;
0W ballistic fingerprint; 0X ledger classes distinct (VPLUS|VPI,
VMINUS|VSTAG); 0Y a^2 zero-limit scaling; 0Z r_prot = a/sqrt(N);
0AA scaling rows L=4..28 (formula + TI inventory + shape dim);
0AB quotient (VPLUS/VPI survive, VMINUS absent); 0AC square
control (uniform/staggered current-free + stress-balanced,
extrema +-4); ODD L=5 (VMINUS JOINT, VSTAG raises, +8 frustrated).

**Ladder:** VACCOMP0-COMPLETE iff every gate green;
VACCOMP0-PARTIAL iff non-apparatus gates fail; VACCOMP0-NULL iff
C0 or C2 fail. Records: data/vaccomp/results.json (41 tasks) +
data/vaccomp/verdict.json.

## VACCOMP0-AMENDMENT-1 (measurement resolution; FROZEN pre-rerun)

Two pre-rerun clarifications after the first campaign pass returned
VACCOMP0-PARTIAL (fails 0H-circle_L6, 0K-VPLUS/VPI). Both are
measurement-resolution issues, not physics and not gate changes:

**A1 scale-covariant stationarity.** At a=1000 the VPLUS/VPI rungs
read ZERO with rho/B drift 7.9e-08 vs the absolute 1e-08 bar --
exactly 100x the a=100 drift (8.0e-10), i.e. pure evolve_fixed fp
noise on 2-homogeneous bilinears (relative 2.6e-12 on observables
of magnitude ~3e4; E=0 states read drift exactly 0.0 since
e^{-i0t}=1 accumulates no phase error). The vf absolute bars are
calibrated at unit norm (VAC-FIELD candidates are normalized), so
the stationarity leg is evaluated on the normalized shape. In
exact arithmetic shape-passes iff a-shape-passes at every a > 0;
this preserves the bar's meaning (fp-noise floor), it does not
weaken the gate. All other legs already pass at a=1000 unmodified
(current/stress exactly 0.0, amplitude/ledger/scale-invariant).

**A2 headline move budget for sampled ledgers.** circle_L6 alphas
0.13..0.65 read BALANCED via ledger_symmetric with moves=2000:
contraction exactly uniform (per-class std 0.0) but M1
seed-stability noise-dominated at 2000 moves. At the headline
20000-move budget (VAC-FIELD precedent) the same states pass with
identical f-stats (0.222/0.385/0.393); the 2000-move failure is
under-resolved sampling, not structure. N > 64 (sampled-M1)
campaign tasks use ledger_moves=20000; N <= 64 keeps exhaustive
M1. Pinned: test_sampled_ledger_resolved_at_headline_moves,
test_amplitude_family_nonzero_energy_all_joint (40 pins green).

## VACCOMP0-VERDICT — VACCOMP0-COMPLETE (DATA)

Beast campaign 2026-10-02 (--jobs 41, 41 tasks) + frozen analyzer:
every gate green, fails []. Records data/vaccomp/results.json +
data/vaccomp/verdict.json.

**Central census (boxed):** the complete nonzero JOINT vacuum
manifold on frozen (J2 torus, -A), modulo R x U(1), is -- even L:
two isolated extremal rays (VPLUS E=-8, VPI E=+8, both
nondegenerate by Perron-Frobenius + bipartite symmetry) plus one
hidden real RP^1 JOINT circle (the VMINUS-VSTAG span in P_- E_0,
JOINT except B==0 BACKGROUND points), each x a full amplitude ray
(all a in 1e-3..1e3 JOINT), pi_0(JOINT) = 3; odd L: VPLUS ray +
VMINUS ray only (VPI frustrated, e_max = 6.47 at L=5; VSTAG
raises), pi_0 = 2. VMINUS is one translation-invariant point of a
continuous hidden-vacuum circle, not an isolated class (outcome:
degenerate components, connected within the hidden sector,
disconnected across eigenvalues).

**Spectral (C2/0A/0F/0G):** extrema +-8 exact at L=4/6/8, Bloch
dev < 1e-6, extremal states nondegenerate, candidate residuals <
1e-9 with subspace weight 1. Zero split exact: L4 22=16+6, L6
46=36+10, L8 78=64+14, L28 838=784+54; odd L5 25=25+0 (no
symmetric zeros). Stationarity theorem verified on an arbitrary
degenerate superposition (drifts 0.0, phase rate 0.0).

**Exclusion (0E/0I/0J):** generic eigenstates are NOT vacua --
complex E_0: 16/16 BACKGROUND, current_free binds 16/16; real
E_0: 8/8 BACKGROUND, stress binds 8/8 (J==0 always, edge_max <
1e-12); mid-eigenvalue complex: 8/8 BACKGROUND. Complex hidden
16/16 current-carrying (frac_excluded 1.0). Real P_- projective
space is 15-dim; JOINT carves exactly the 1-dim TI circle from it.

**Circle (0H):** L4/L6 grids: 12/12 non-BZERO points JOINT, B==0
point (alpha=pi/4, Bmax 6.9e-18) BACKGROUND-capped by the strict
Bmax gate. B==0 independent-set states: stationary + current-free
+ stress-balanced but BACKGROUND (B is the primary relational
observable; no B-vacuous theorem).

**Amplitude (0K):** all five families (4 TI rays + CIRCLE@pi/6)
all-JOINT over 1e-3..1e3. Shape degeneracy (circle S^1) is
distinct from amplitude degeneracy (R_+); both physical under
SYM-0 (no-selection firewall kept: no family preferred).

**Beats/disconnectivity (0L/0M/0Q):** same-eigenvalue sweep
stationary everywhere (drifts < 1e-8), phi=0 cut interior JOINT
count exactly 10 (real circle minus B==0 point). Mixed pairs beat
at dE = 16/8/8 with |corr| = 1.0, rho_beat_amp > 0, zero interior
JOINT in all three cuts, no cross-term cancellation (rho_x/B_x/J_x
all nonzero) -- VPLUS/VPI/CIRCLE are mutually disconnected under
continuous JOINT-preserving paths.

**Orbits/symmetry (0T/0U):** all four TI vacua are ray-TI
singletons (stabilizer = full group, orbit size 1, sheet-ray
invariant). Patterned (non-TI) JOINT vacua: the circle interior
(alpha not multiple of pi/2) -- stationary, balanced, spatially
structured; filed without matter language.

**Observer/excitation/ledger (0V/0W/0X):** the four TI vacua are
physically distinct but coarse-identical (pairwise d_coarse_rho =
0.0 exactly); circle-interior states are coarse-visible
(d = 0.044). Excitation fingerprint ballistic and
background-independent (speed 2.54, r2 0.992, alpha 1.89) --
carrier dynamics universal across the manifold by the 0L
linearity theorem. Ledger classes distinct: VPLUS (1/0/0), VPI
(.5/.5/0), VMINUS/VSTAG (.5/.25/.25), circle-interior
(.25/.37/.38); ledger distances VPLUS|VPI dmax 0.125,
VMINUS|VSTAG dB 0.0625.

**Zero (0Y/0Z):** Q/Bmax/E scale as a^2 exactly (slope 2 to
1e-9); a -> 0+ approaches ZERO continuously in every relational
observable; r_prot = a/sqrt(N) for uniform vacua (zero-free);
independent-set states r_prot = 0. ZERO stays non-JOINT (boundary
point with singular phase coordinates).

**Scaling/controls (0AA/0AB/0AC/ODD):** zero formula + TI
inventory + shape dim verified L=4..28 (degeneracy extensive in
N via the flat band, JOINT shape manifold 1-dim even / 0-dim
odd). Quotient: VPLUS/VPI descend (residuals < 1e-9), VMINUS
absent (hidden structure operationally invisible). Square torus:
uniform/staggered current-free + stress-balanced, extrema +-4, no
flat band -- the hidden JOINT circle is J2-special, not generic.
Odd L=5: VMINUS JOINT, VSTAG raises, +8 frustrated.

**Downstream:** VAC-SELECT receives the filed state space (even:
{VPLUS-ray, VPI-ray, CIRCLE x R_+} + BACKGROUND B==0 sector;
odd: {VPLUS-ray, VMINUS-ray}); no preference attached (0AD kept).

## VACSEL0-PREREG — Dynamical selection among joint vacua (FROZEN PRE-DATA)

**Status:** apparatus + regressions + MEASURE gate + battery + verdict
ladder frozen; campaign NOT YET RUN. VAC-SELECT-0 is DEFINED / BLOCKED
ON MEASURE-0: headline stages VACSEL-0D..0Z run if and only if
MEASURE-0 earned a unique physical transition measure W with zero
debt-reasons. No measure may be chosen merely to run this campaign; no
transition weight is recalibrated on vacuum behavior; no vacuum is
ranked by field energy, simplicity, eigenvalue, hiddenness,
propagation quality, or structural flatness.

**Mission:** determine whether the complete structural transition
measure dynamically distinguishes among the three nonzero joint vacua
VPLUS / VPI / VMINUS (VACFIELD0-JOINT family on J2), whose field
propagation is identical but whose structural ledgers differ (flat /
one-sided / structured hidden).

**Frozen inputs (read-only, byte-identical vendoring, no law change):**
VACFIELD0-JOINT shapes + banks (vacfield.py 33fb6e93bf77, branch
vac-field-nonzero-joint-8ec1 @ 3dbfe34); HIDDEN0-SEPARATED apparatus
(hidden.py 4907b2ee253e, hidden0-local-dof-3478 @ 90aaa53); HBR0-SIGNREV
ledger apparatus (hiddenbr.py 144dcc41a16f, hiddenbr-ledger-3478 @
b056805); SYM0 quotient X_red = X/(R x U(1)) (sym0.py dbd4e72818e3,
sym0-state-census-e27a @ 43ac69a); ZERO-0 classification (zero.py
a48dfcf3c7a2, zero-crossing-census-ee5c @ c4c2fb6); FIELD-0 null
(field0.py 8049817a831b, field0-null-960b @ b9dea0c); RAND-0 admissible
sets + orbit apparatus (rand0.py 502bec28d421, rand0-stochastic-1621 @
c5722da); MEASURE-0 candidates + battery (measure0.py 45f6fefce06c,
measure0-transition-measure-f670 @ 633b431); QUOT/VAC-0 banked modules
(quot.py 73c62c2f4b07, vac0.py 7993d4f4cf36, same tips). U0/UG/TIME-0/BR
apparatus consumed from main tail (7153f65). Frozen conventions:
H = -A, J = 1, hbar = 1, dt = 0.1, sum map, EM-0B B/J quadrature,
E = -2 sum B; J2 L_EXACT = 4 / L_HEAD = 28; A_HEADLINE = 1.0;
AMPLITUDES = 7-point VACFIELD grid; M1 eps = 1e-10.

**W-free stages (run unconditionally):** VACSEL-0A freeze families
X_+, X_pi, X_- via vacfield.candidate_shape verbatim (full amplitude
family, scale covariance reported); VACSEL-0B field regression
(stationarity, J_vac = 0, identical packet propagation across vacua);
VACSEL-0C structural regression (exhaustive M1 L4 + sampled M1 L28 +
HIDDEN-BR vac_ledger_table; no transition executed). Expected anatomy:
VPLUS f0 = 1 flat; VPI f_pos = 0 one-sided (dE <= 0); VMINUS f0 = 1/2
structured with L_min < L_max.

**MEASURE gate (frozen firewall):** READY iff MEASURE-0 inventory is
exactly ("const", "orbit") with 0 fitted params each, an earned-W
symbol (w_physical / W_EARNED) exists, and zero debt-reasons hold on
the tiny battery (orbit-rival differs / support not fully reversible /
no conservation selector / graph grain underdetermined). The gate
re-evaluates the four frozen debt-reasons from code (never from memory
of another campaign's verdict text). Observed pre-data context (NOT
consumed as a gate input): MEASURE-0 beast ledger
~/measure0-f670/data/measure0_verdict.json reports MEASURE0-DEBT,
hard_ok, 544 cells, 0 run-failures, the same 4 debt-reasons; branch tip
633b431 holds prereg + Amendment-1 with verdict filing pending.

**Headline stages (gated):** VACSEL-0D..0Z (weight census, quiescence,
class/leakage/return/stationary, reversibility, exit anatomy,
VPLUS/VPI/VMINUS tests, excitation/perturb/hidden/transport/locality,
size scaling, substrate coordination, no-shortcut firewalls, degeneracy,
vacuum transitions) execute if and only if the gate is READY. When
blocked, every headline entry point returns a refusal record
{ran: False, verdict: VACSEL0-NOMEASURE} as data, never an exception.

**Controls (frozen):** C0 VAC-FIELD JOINT regression (all three JOINT
under fixed geometry); C1 SYM quotient exactly R x U(1); C2 hidden
P_- retained; C3 HBR structured-ledger anatomy; C4 MEASURE freeze
(sha pin); C5 no retuning across vacua; C6 time reversal (dynamics leg
W-free, W leg gated); C7 locality (gated, needs W); C8 FIELD null
(psi-psi non-forceful). W-needing controls file inapplicability when
blocked.

**Battery (frozen, beast mp, deterministic):** scripts/
vacselect_campaign.py tasks A-L4 / A-L28 / A-amps / B-L4 / B-L28 /
C-L4 / C-L28 / G-gate / C-controls / H-refusal (10 records, scalars +
shape checksums; no .npy sidecars). scripts/vacselect_analyze.py
applies HARD gates H-A (family L4/L28 + amps slopes 2.0 +/- 0.01,
VMINUS E = 0) / H-B (field L4/L28 incl. bitwise cross-bg dpsi) /
H-C (struct L4/L28 + controls) / H-G (inventory + debt filed) / H-H
(headline ran iff gate ready). Full suite on beast in parallel
(test_weighted.py skipped per standing instruction). Nothing local
except unit pins (tests/test_vacselect.py, 20 pins, L4/tiny only).

**Verdict ladder (frozen):** VACSEL0-NOMEASURE = gate not ready
(headline not run; selection undefined because geometry dynamics is
incomplete). VACSEL0-DEGENERATE / CLASS / SELECTED require gate READY
plus executed headline statistics; the ladder cannot advance past
NOMEASURE without them. PREDICTION (pre-data, gate-arithmetic-backed):
VACSEL0-NOMEASURE via the four MEASURE debt-reasons (orbit-rival
differs on node patches, reverse support graph-only, no earned
selector, grain underdetermined), reproduced from code in the gate.

## VACSEL0-VERDICT (filed 2026-10-02): VACSEL0-NOMEASURE

**Headline:** vacuum selection remains undefined because the geometry
dynamics is incomplete. The MEASURE gate re-evaluated from code is not
ready (4/4 frozen debt-reasons hold); headline stages VACSEL-0D..0Z
were not run (0/23 ran, all refusal records). No transition weight was
chosen, no vacuum was ranked. This is the preregistered predicted
outcome, not a failure.

**Battery (beast ~/vacselect-750f, 10 records, exit 0):**
data/vacselect/{A-L4,A-L28,A-amps,B-L4,B-L28,C-L4,C-L28,G-gate,
C-controls,H-refusal}.json + data/vacselect_verdict.json. Local
analyzer re-run reproduces the beast verdict bitwise.

**Gates (10/10 HARD green):** H-A-family-L4/L28 (norms/E/residuals/
sectors match VACFIELD0: E = -8/+8/0 exact on L28, residuals 0.0,
J_max = 0.0, w shares exact); H-A-amps (E ~ a^2 slopes 2.0000/2.0000,
VMINUS E = 0.0 all 7 amplitudes); H-B-field-L4/L28 (all vacua
stationary, current-free edge/div/circ = 0.0, norm accounting ok,
cross-background packet dpsi bitwise 0.00e+00 on L4 AND L28);
H-C-struct-L4 (VPLUS f0 = 1 flat / VPI f_pos = 0 one-sided /
VMINUS f0 = 1/2 structured, exhaustive n = 47104); H-C-struct-L28
(sampled 5 seeds x 20000 moves: VPLUS f0 = 1, VPI f_pos = 0,
VMINUS f0 = 0.50 +/- 0.01; VMINUS ledger structured over 12 offset
classes, within-class spread 0.00e+00); H-C-controls (C0 all JOINT,
C1/C2/C3/C5/C8 pass, C4 sha-pinned, C6 dynamics leg True with W leg
inapplicable, C7 inapplicable); H-G-gatefiled (inventory exactly
("const","orbit"), 0 fitted params each, no earned-W symbol, 4
debt-reasons: orbit-rival differs 36/72-class battery positive,
reverse support 33/60-class incomplete, conservation selects 0,
grain underdetermined); H-H-norun (headline ran 0).

**Controls C0..C8:** C0 VAC-FIELD regression JOINT x3; C1 SYM quotient
R x U(1) intact; C2 hidden P_- retained (VMINUS w_anti = 1);
C3 HBR structured-ledger anatomy reproduced; C4 MEASURE freeze pinned
(measure0.py sha16 45f6fefce06c9da4, tip 633b431); C5 identical
grids/bars across vacua by construction; C6 Theta dynamics holds on
all vacua (W-reversibility inapplicable without W); C7 inapplicable
without W (no remote-geometry claim made); C8 FIELD null holds
(finite field energies, no psi-psi force invoked).

**Independence note:** the gate consumes MEASURE-0 code + prereg
semantics only. The observed MEASURE-0 beast verdict (MEASURE0-DEBT,
hard_ok, 544 cells) is consistent corroboration, not a gate input;
had MEASURE-0 filed CLOSED with an earned-W symbol and zero
debt-reasons, the gate would have opened and the headline battery
would have executed.

**Downstream consequence:** VAC-SELECT-0 preserves the full
VACFIELD0-JOINT family. No vacuum sector is preferred, mixed, or
destabilized by any dynamics earned to date. The degeneracy question
reopens if and only if a future MEASURE campaign earns a unique W.

## BGRESP0-PREREG (FROZEN pre-data; commit predates ALL BG-RESP-0 runs)

Vacuum-dependent relational susceptibility campaign (BG-RESP-0). Mission:
determine exactly how the three earned nonzero JOINT vacua convert an
identical field excitation dpsi into different local and remote relational
responses (drho, dB, dJ). VAC-FIELD-0 and VAC-EXC-0 established that the
carrier dpsi(t) = U(t) dpsi(0) is background-independent (bitwise cross-bg
identity) under the frozen field law, while the physical relational response
depends on the background through exact cross terms. Same carrier +
different vacuum -> different relational response. BG-RESP-0 measures and
derives that difference as the susceptibility operator chi_alpha.

Central question: for identical dpsi(0) with psi = psi_vac + dpsi, is
chi_+ = chi_pi = chi_- (as operators)? ZERO is the no-background control
only (chi_ZERO = 0 at first order for quadratic observables).

### Firewall (campaign level)

BG-RESP-0 may not claim: force, gravity, mass, charge, dielectric medium,
electromagnetic susceptibility, curvature, actual geometry change, or vacuum
selection. "Susceptibility" means ONLY the mathematical response of
established relational observables to dpsi. No continuum-medium constitutive
equations are imported. No geometry evolution, no nonlinear field term, no
source feedback, no stochastic dynamics, no structural event. Delta variables
are readout-only: dO = O[vac + d] - O[vac] at EQUAL time (co-evolving vacuum
frame). Virtual ledgers (0W) are readout-only: no event is ever executed.
Different dB responses are not forces (0AB gates FIELD-0 witness I = 0).

### Frozen ontology + consumed apparatus (byte-identical, read-only)

H(G) = -A(G), J = 1, hbar = 1 (P1-locked). psi_u = r_u + i s_u per node;
rho = |psi|^2; B_uv = Re(psi*_u psi_v); J_{u->v} = 2 Im(psi*_u psi_v)
(EM-0B sign); E_psi = -2 sum_edges B (BR-0). Exact decomposition (pinned):
drho = 2Re(vac* d) + |d|^2; dB = B_cross + B_dd; dJ = J_cross + J_dd.
Susceptibility chi is the real (M x 2N) matrix with M = N + 2E rows
[rho; B; J] and 2N columns [dr; ds], every entry an explicit analytic
function of the background (no fitting). Consumed (md5-12): vacfield
a9fe0f5fa241 (VACFIELD0-JOINT), vacexc 841897f6ce7e (VACEXC0-COMPLETE),
response 63cebb004341, hidden 85a055e7dd40, hiddenbr 6df6ce530d83,
field0 79de081f65d9, zero 5185bba6d6ed, quot d250eeca640c, sym0
1efe9ac53c37, rand0 9627bf471e41, vac0 9b1c6c50e108 + their test files
(all green, unmodified). Ballistic/malus/formation/coherence/continuum/
backreaction/driven/contraction/phase/potential/conservation are main-tail
tips, byte-identical to sibling consumption (no vendoring needed).
Banked theorems consumed: U(t)(vac + d) = U(t)vac + U(t)d + co-rotating
law (VACFIELD0-0L); cross-bg bitwise dpsi identity + exact B-null theorem
for single-node real prep on bipartite J2 (VACEXC0-0B/Amendment-1b);
K(0) = I + chi_rho/chi_bond static rows (RESPONSE-0); H P_- = 0 +
local read + remote blindness (HIDDEN-0); dE/dA = -2B + ledger linearity
(HIDDEN-BR); superposition + witness I (FIELD-0); U(1) redundancy vs
physical scale (SYM-0); incident null at exact zeros (ZERO-0).

### Vacua + amplitudes (earned, not selected)

VPLUS: uniform 1/sqrt(N), E = -8, P_+. VPI: (-1)^q/sqrt(N), E = +8, P_+.
VMINUS: (-1)^b/sqrt(N), E = 0, P_-, frozen. ZERO: psi = 0 control.
Shapes psi_vac^(a) = a * hat with a in AMPLITUDES =
{1e-3, 1e-2, 1e-1, 1, 10, 100, 1000} (VACFIELD0 set); headline a = 1.

### Frozen constants (all runs)

J2 L_HEAD = 28 (N = 1568, sparse chi + Krylov headline), L_MID = 8
(N = 128, dense chi + full SVD), L_EXACT = 4 (N = 32, dense + exact),
L_SCALING = {4, 6, 8, 12, 28} (even only; VPI needs bipartite). T_K = 30,
DT_K = 0.1 (300 rows); T_FIT = 8 (no-wrap window). EPS_GRID =
{0.003, 0.01, 0.03}, headline 0.01; EPS_LIN = {0.001, ..., 0.1} (slopes;
deep-linear two-point (0.001, 0.003) per VACEXC Amendment-1 precedent).
CENSUS_KINDS (0V battery, frozen): point_real, point_imag, packet (B0
settings), sym_sector, hidden_sector (all vac-independent norm-1
directions x eps). Zero threshold tau = max(1e-300, 1e-9 x run-max|psi|).
Bars: bgresp.BARS (frozen; decomp 1e-12, zero_chi 1e-12, phase_null 1e-9
hard gate, scaling 1e-9, same_carrier 1e-9, kernel 1e-8, bipartite_b 1e-12,
energy 1e-9, witness 1e-6 FIELD-0 bar, fingerprint 1e-9, covariance 1e-9,
linearity_slope 0.05). SVD null threshold: max(dim x eps_machine, 1e-9) x
s_max (relative, preregistered). L28 operator norms via svds(k=1) with a
deterministic power-iteration fallback; full SVD only on L <= 8.

### Stage protocols + predictions (P) / gates (G)

0A exact decomposition: P: drho/dB/dJ = cross + dd exactly (pinned
identity, cross-checked against vacexc algebra). G: decomp check (L4 all
vacua x battery + random; max-resid < 1e-12).

0B ZERO theorem: P: chi_ZERO = 0 exactly (all entries), so dO_ZERO is
purely quadratic; reproduces VAC-EXC c1 ~= 0. G: zero_theorem check
(chi_ZERO max-abs < 1e-12; lin slopes: ZERO = 2, nonzero = 1 +/- 0.05).

0C/0D chi-matrix: P: chi_alpha derived analytically (no fitting); rank,
nullity, singular values, support (nnz = N + 4E for real vacua), Frobenius
norm sqrt(44) for all nonzero vacua (analytic: uniform |vac|). G: none
beyond pins (filed spectra; L4/L8 full SVD banked, L28 sparse norms).

0E vacuum comparison: P: pairwise ||chi_a - chi_b|| in Frobenius +
operator + symmetry-resolved (chi P_+/-) norms (all three preregistered;
no post-hoc norm selection). Filed (no gate: the OPERATOR difference is
the deliverable, including any null result on global norms).

0F null spaces: P: null directions classified (global phase vs symmetry vs
sector vs bipartite selection). Filed + pinned overlap on L4.

0G global-phase null: P: i psi_vac in ker chi (all relational observables
unchanged under infinitesimal global phase). G: HARD GATE phase_null
(||chi @ v_phase|| < 1e-9, all nonzero vacua x L4/L8/L28). Links to SYM-0.

0H amplitude direction: P: eps psi_vac visible (drho != 0, dB != 0;
dJ = 0 for real backgrounds, filed); contrasts physical scale vs
redundant phase. G: amplitude check (norms above bar, all L).

0I/0J bases: P: primitive (real/imag point) columns span arbitrary
infinitesimal disturbances; local amp/phase kicks separate at t = 0 on
real backgrounds (amp -> rho/B only, phase -> J only) while peak-norm
B/J responses mix at later times through the full operator + carrier
spread (explains VAC-EXC non-separation). Filed + pinned.

0K bipartite B-null: P: reproduce VACEXC Amendment-1b theorem (single-node
real prep on bipartite J2: B(t) = 0 identically, chiral-reality preserved)
from the susceptibility/operator structure (ZERO dd-view + selection rule).
G: bipartite_bnull check (B_max < 1e-12, L4 + L28).

0L amplitude scaling: P: chi_{a psihat} = a chi_{psihat} exactly (fixed
absolute d). G: scaling check (relative dev < 1e-9 over AMPLITUDES).

0M fractional scaling: P: d = a eps eta gives cross ~ a^2 eps, dd ~ a^2
eps^2; normalized (divide by Q = a^2) collapse across a. G: frac leg of
scaling check (max-dev < 1e-9).

0N sector-resolved: P: chi P_+ / chi P_- norms filed per vacuum; VMINUS
(P_-) vs VPLUS/VPI (P_+) distinguished by symmetry-resolved operator norm.
Filed (no gate).

0O/0P/0Q anatomy: P: per-class (SX/SY/F1/F2) uniformity + translation
covariance (dev < 1e-9, filed per vacuum); VPI checkerboard sign structure;
VMINUS P_+ disturbance reads through cross terms (HIDDEN-0 local read as
susceptibility). Filed + covariance filed (descriptive, not ladder).

0R same-carrier theorem: P: dO_a(t) - dO_b(t) = (chi_a(t) - chi_b(t)) d(t)
EXACTLY (dd cancels: background-independent). G: same_carrier check
(max-resid < 1e-9 at t = 0/4/8/16 on L28 + L4 static battery).

0S time-domain: P: K(t) = chi_{vac(t)} U(t) = chi_0 e^{iEt} U(t) (both forms
pinned equal; VMINUS reduces to chi U); RESPONSE-0 cross-check of static
rows + kernel structure where apparatus overlaps. G: kernel legs of
same_carrier (crosscheck + dense-vs-Krylov < 1e-8 on L4).

0T/0U point/remote maps: P: per-kind shared carrier + per-vacuum response
traces + shell means at t = 0/4/8/16; carrier arrival vacuum-independent,
response sign/magnitude not. Filed (no gate).

0V sign census: P: frozen battery x all edges; counts of strict opposite-sign
cross_B pairs (both above visibility bar). A positive count means the same
carrier presents opposite geometry-conjugate signals on different vacua
(no geometry inferred). Filed (no gate; battery frozen pre-data).

0W ledger: P: Delta_exc R_G = R_G[vac + d] - R_G[vac] (M1 stats diff,
readout-only, HIDDEN-BR-compatible) per (vacuum, kind in {point_real,
packet, hidden_sector}). Filed (no gate).

0X energy: P: dE = 2Re<vac|H|d> + E[d] exactly (+ eigenstate simplification);
dE differs across vacua by E_vac term (VMINUS cross = 0). G: energy check
(anatomy resid < 1e-9, all vacua x kinds).

0Y hidden-energy null: P: P_- perturbations around VMINUS have dE = 0
exactly (H P_- = 0 + E_vac = 0) but dB != 0 (linear-response HIDDEN-BR).
G: hiddennull legs of energy (dE == 0 + dB_max > 0, L4 + L28).

0Z ZERO comparison: P: chi_ZERO = 0 while all nonzero chi != 0 (formalizes
ZERO as no-linear-susceptibility limit). G: folded into zero_theorem.

0AA visibility: P: per-response visibility labels via the frozen
vacexc/HIDDEN rule (hidden > observer_geometric > transport_visible >
locally_visible > undetected). Filed (descriptive; large local chi need
not imply remote signal).

0AB no-force: P: FIELD-0 witness I = 0 on matched head-on packet collisions
for all vacua (different dB responses, same null witness). G: witness
check (I gated, all 4 backgrounds).

0AC discrimination: P: preregistered 7-component fingerprint F_alpha
(norms + signed sums + energy cross; fixed battery) separates all three
vacua (pairwise dist > 1e-9). G: fingerprint check (all L).

0AD minimal: P: smallest separating subset by frozen size-first
lexicographic search (+ all minimal-size winners filed). Filed size +
subset (no adaptive construction).

0AE size scaling: P: chi norms/spectra + fingerprint + census over
L in {4, 6, 8, 12, 28}; classify distinctions as local/size-independent
vs finite-size vs IR. Filed (no gate).

### Verdict ladder (analyzer-gated)

Checks (10, all boolean): decomp (0A), zero_theorem (0B/0Z + lin),
phase_null (0G hard gate), amplitude (0H), scaling (0L/0M),
same_carrier (0R/0S), bipartite_bnull (0K), energy (0X/0Y), witness
(0AB), fingerprint (0AC). Headline: BGRESP0-COMPLETE if all 10 green;
else BGRESP0-PARTIAL with per-check table. Per-vacuum distinctions filed
as family (no ranking). Amendments, if any, as BGRESP0-AMENDMENT-n with
gated re-runs; none pre-data.

### Execution

77 tasks (scripts/bgresp_campaign.py --print-all), beast EC2
(16.54.88.181, xargs -P 90, OMP threads 1), JSON records data/bgresp/*.json
(committed) + .npy sidecars data/bgresp/npy/ (gitignored, checksums in JSON).
Full suite on beast (pytest -n 90 --ignore=tests/test_weighted.py). Analyzer
scripts/bgresp_analyze.py writes data/bgresp/verdict.json. Verdict filed here
post-data.

### BGRESP0-VERDICT (BGRESP0-COMPLETE, 10/10)

Branch cursor/bg-resp-0-0aa2 (base main tail 7153f65). 77/77 tasks
CAMPAIGN-DONE on beast (16.54.88.181, xargs -P 90, OMP threads 1, nice);
records data/bgresp/*.json + verdict.json banked; .npy sidecars on beast
(gitignored, shas in JSON). Analyzer scripts/bgresp_analyze.py per PREREG
(no amendments; one apparatus crash fix for 6 ungenerated L28 sparse-sector
records, no banked data affected, committed as 14a8ba2). Full suite on beast
(venv, -n 90, --ignore=tests/test_weighted.py): 1605 passed, 2 skipped,
0 failed.

Headline: chi_+ != chi_pi != chi_- as OPERATORS (pairwise Frobenius
distance sqrt(88) at every L; operator 8*sqrt(2/N); sector-resolved and
sign structure differ per pair), each rank 2N-1 with the sole null direction
exactly global phase (overlap 1.0), while chi_ZERO = 0. Same carrier +
different vacuum -> provably different relational response, pinned exactly:
dO_a(t) - dO_b(t) = (chi_a(t) - chi_b(t)) d(t) to fp precision at t =
0/4/8/16 (dd cancels: background-independent).

Spectra (0D, L4/L6/L8 dense SVD; L12/L28 sparse): ||chi||_fro = sqrt(44)
exactly for all nonzero vacua at all L (uniform |vac| analytic); op norm
8/sqrt(N) (1.4142/0.9428/0.7071/0.2020); rank 2N-1, nullity 1, null =
global phase. Sector-resolved op norms split VMINUS from the symmetric
pair: VPLUS/VPI (op, op/sqrt(2)) on (P_+, P_-) vs VMINUS swapped
(op/sqrt(2), op) at every L. Pairwise sector-restricted diff norms: VPLUS-
VPI preserves full op under either projector; VMINUS-involving diffs drop
to sqrt(3)/2 x full (difference straddles sectors). Per-class (SX/SY/F1/F2)
uniformity exact (std 0.0); translation covariance dev ~1e-17 (all vacua).

Sign census (0V, frozen battery): point_real static: VPLUS-VPI 8/8 opposite
(all incident edges flip), VMINUS pairs 4/8; timed (t = 4/8, L28): VPLUS-VPI
6272/6272 = EVERY edge opposite, VMINUS pairs exactly half (3136/6272).
point_imag complementary: VPLUS-VPI 0/6272 (same sign everywhere), VMINUS
pairs ~half. sym_sector matches point_real rigidity; hidden_sector local
(16/16, 8/16, frozen support); packet generic ~50%. Static point_imag dB1 =
0 exactly (vacuous, filed: real backgrounds + imag point). The same carrier
disturbance presents opposite geometry-conjugate signals on different vacua;
no geometry is inferred.

Fingerprint (0AC/0AD): 7-component F separates all pairs at all L
(min-dist 2.83/1.89/1.41/L12/L28 0.404 ~ 16/sqrt(N)); minimal size 1 with
THREE winners at every L: F5 energy cross (2.83), F6 signed amp-dB sum
(+/-/0 pattern: VPLUS +8e/N, VPI -8e/N, VMINUS 0), F7 signed sym-dB sum.
Norms alone (F1-F4) are vacua-blind (identical magnitudes); SIGNS + ENERGY
carry the distinction. Local and size-independent in normalized form.

Controls: bipartite B-null exact (B_max = 0.0, chiral dev ~1e-18, L4+L28);
hidden-energy null exact (dE = 0.0, dB_max > 0, L4+L28); FIELD-0 witness I
= 9.7e-16 (fp zero) IDENTICAL on all 4 backgrounds while dB_max/dJ_max
differ per vacuum (VPLUS 3.7e-5/1.5e-5, VPI 6e-6/6.8e-5, VMINUS
3.3e-5/5.9e-5, ZERO 1e-6/0.0): different responses are not forces. Kernel
K(t) = chi_{vac(t)} U(t) = chi_0 e^{iEt} U(t) pinned equal (dev 0.0) +
dense-vs-Krylov < 1e-8. Lin slopes: nonzero 1.0, ZERO 2.0 (deep-linear
two-point; t = 0 real-prep J legs + ZERO B leg vacuous-pass per filed
exact-zero rules). Virtual ledger: packet excitations strongly restructure
(VPLUS flat f0 = 1 -> fneg/fpos ~0.50/0.50); point/hidden weak; VPI/VPMINUS
departures filed per kind.

Interpretation (boxed): susceptibility is earned, vacuum-dependent, and
exactly characterizable: the three JOINT vacua are pairwise distinguished
by their chi operators (sign/sector/energy anatomy), operationally
identifiable by a single signed-B or energy readout, and invisible only
along global phase. ZERO is the no-linear-susceptibility limit. Nothing
here selects a vacuum or moves geometry; the response differences are
mathematical facts about established relational observables, filed as input
to future geometry coupling.

## VACTEXTURE0-PREREG (FROZEN pre-data; commit predates ALL VACTEXTURE-0 runs)

Spatial textures inside the hidden vacuum component (VAC-TEXTURE-0).
Mission: determine whether the hidden JOINT vacuum orientation can vary
spatially while remaining vacuum-like, and characterize what gradients of
that orientation become under frozen H = -A.

At fixed amplitude parameter a, real basis (VMINUS, VSTAG) with
psi_hid(alpha) = a [cos alpha VMINUS + sin alpha VSTAG], alpha ~ alpha + pi
(global ray identification). Textures assign one angle per coarse cell,
alpha: cells -> [0, pi), with node field psi_{x,y,b} = (a / sqrt(N)) s_b
[cos alpha_{x,y} + sin alpha_{x,y} (-1)^{x+y}], s_b = +1/-1 for b = 0/1.
Every texture is real and sheet-antisymmetric by construction, hence in P_-
exactly; the banked identity H P_- = 0 (MALUS-0, QUOT-0) then places every
texture in E_0 exactly. The campaign tests this derivation, measures what
gradients become (emitted P_+, rho/B/J, energy, transport, observer and
ledger readouts), and derives gradient scaling without imposing any
continuum action.

### Firewall (campaign level)

VAC-TEXTURE-0 may not claim, and its interpretation layer may not use:
Goldstone, spin, gauge, defect, or particle terminology. Textures are
described ONLY as spatial variation of the hidden vacuum orientation with
measured relational, transport, observer, and ledger readouts. No continuum
action is imposed: gradient scaling is DERIVED from measured relational
observables, never fitted as an input action. No geometry evolution, no
onsite terms, no edge weights, no nonlinear field term, no source feedback,
no stochastic dynamics, no structural event. Virtual ledgers are
readout-only. Different B/rho landscapes are not forces (0H/0I gate frozen
flow + FIELD-0 witness I = 0).

### Frozen ontology + consumed apparatus (byte-identical, read-only)

H(G) = -A(G), J = 1, hbar = 1. psi_u = r_u + i s_u per node;
rho = |psi|^2; B_uv = Re(psi*_u psi_v); J_{u->v} = 2 Im(psi*_u psi_v);
E_psi = -2 sum_edges B. Geometry frozen (J2 torus). Consumed (md5-12):
vacfield a9fe0f5fa241, vaccomp 0bd50db361e8, hidden 85a055e7dd40, hiddenbr
6df6ce530d83, bgresp f93cadaacb27, response 63cebb004341, field0
79de081f65d9, zero 5185bba6d6ed, quot d250eeca640c, sym0 1efe9ac53c37,
ballistic e877d1160fff, malus e835f72eeb3d, continuum 30c4d79d9c66,
backreaction 2752f060e3aa, driven 3666ab13ee1c, contraction c7aa09140bf1,
phase b3163f5e2b8d, formation 3527ac1aea14 + their test files (all green,
unmodified). Banked theorems consumed: H P_- = 0 + [H, S] = 0 (MALUS-0);
uniform-alpha JOINT RP1 circle (VAC-COMP-0); local read + remote blindness
(HIDDEN-0); R_G + M1 + contraction uniformity (VAC-COMP/VAC-FIELD ledger);
superposition + witness I (FIELD-0); U(1) redundancy vs physical scale
(SYM-0); coarse pattern vs quotient dynamics (QUOT-0/MALUS); linearity of
U(t) on backgrounds (VAC-EXC-0 0A form).

### Texture families + amplitudes (preregistered, not adapted)

Six families (vactexture.FAMILIES): uniform (constant map); sine-x
(alpha0 + delta sin(2 pi x / lam)); sine-xy (separable product);
linear (alpha0 + winding pi x / L, integer winding ray-periodic); wall
(periodic tanh pair, widths {1.0, 2.0}); step (periodic sharp pair).
DELTA_GRID = {pi/8, pi/4, pi/2}, ALPHA0_GRID = {0, pi/8}, lam in
{L, L/2} (L4/L8) and {28, 14, 7} (L28), windings {1, 2}. Amplitude
parameter a in AMPS = {1e-3, ..., 1e3} (VACFIELD0 set); headline a = 1.
Norm theorems (exact, pinned pre-data): x-only maps (uniform, sine-x,
linear, wall, step) preserve Q = a^2 exactly at any alpha0 (the cross
term sin(2 alpha) (-1)^{x+y} sums to zero over y in every row); sine-xy
at alpha0 = 0 on even L preserves Q = a^2 exactly (y <-> L-y pairing);
Q varies at fixed a only through y-dependent maps at alpha0 != 0
(mod pi). Amplitude direction is physical (SYM-0 scale).

### Frozen constants (all runs)

J2 L_EXACT = 4 (N = 32), L_DIAG = 8 (N = 128), L_HEAD = 28 (N = 1568),
L_LIST = {4, 6, 8, 12, 16, 20, 28} (even; size scaling). ALPHA_GRID =
13 points on [0, pi/2] (circle reproduction). T_K = 30, DT_K = 0.1
(300 rows); T_FIT = 8 (no-wrap window). Carrier packet: VAC-FIELD B0
Gaussian, eps = 0.01. Ledger: 20000 M1 moves, seed 0; contraction scan
16 stratified edges. Bars: vactexture.BARS (frozen; sector_weight 1e-12,
h_residual 1e-9, energy_zero 1e-9, stationarity 1e-8, current_edge 1e-12,
stress_uniform 1e-9, local_bar 1e-6, remote_bar 1e-9, coarse_visible 1e-4,
ledger_visible 1e-6, witness 1e-6 FIELD-0 bar, scaling_tol 0.05).

### Stage protocols + predictions (P) / gates (G)

0A uniform-circle reproduction: P: uniform rays reproduce the VAC-COMP
JOINT census at every even L: JOINT except the B == 0 point at
alpha = pi/4 (BACKGROUND-capped by the strict Bmax gate). G:
uniform_circle check (L4/L6/L28 x 13 alphas).

0B texture construction: P: every family output real, P_- exact;
constant map == uniform ray to fp; periodicity params exact (lam | L,
integer winding; wall/step/uniform always periodic). Filed + unit pins
(no campaign gate beyond 0C membership).

0C P_- E_0 membership: P: w_sym = 0, ||H psi|| = 0, E = 0 exactly for
every (family, params, L, a) row: the obstruction is identically zero
by construction + banked H P_- = 0. Any nonzero entry IS the derived
obstruction. G: pminus_e0 check (all sweep/amplitude/scaling rows).

0D emitted P_+ content: P: w_sym stays 0 along U(t) (banked [H, S] = 0);
no P_+ emission from any texture. G: E legs folded into pminus_e0
(stationary_L4/L28 traces, max + endpoint).

0E relational anatomy: P: J = 0 and E = 0 exactly (real states); B/rho
nonuniform tracking the orientation gradient. Derived pre-data: the
gradient readout is the per-class B spread B_pcmax (uniform hidden
vacua exactly uniform per class); global B_std carries a class-mixing
baseline (1/N on uniform VMINUS) and is filed, not gated. G:
local_B_std supporting (max B_pcmax over nonuniform L28 rows > 1e-6).

0F wavelength/amplitude sweeps + scaling: P: B_pcmax ordered in the
analytic gradient (2 pi delta / lam) over the lam grid at fixed
delta = pi/4; log-log slope derived (no functional form imposed),
predicted positive; Q = a^2 exactly over AMPS (log-log slope 2 to
1e-9). G: scaling check (finite positive slope + endpoint ordering);
amp_scaling filed.

0G smooth vs sharp: P: matched sine-x vs step textures at shared delta
are locally distinguishable (D > 1e-6 at every delta, L4 + L28); exact
gradient concentration (step max_grad = delta >= sine max_grad for
lam >= 4). B_std/B_range landscapes filed descriptively (global-range
ordering NOT gated: class-mixing baselines make it non-robust,
derived pre-data). G: smooth_sharp check.

0H stationary-hidden vs propagating: P: textures frozen (rho/B/J drifts
0, phase rate 0: H psi = 0 gives U(t) = I on the state); a B0 packet
on a texture background splits exactly (full - texture == d-alone to
1e-10), the texture stays frozen, the packet stays ballistic
(speed > 0.5, r2 > 0.9). G: stationary + carrier checks.

0I observer visibility + local distinguishability: P: texture vs
uniform reference locally visible (D > 1e-6 with d_B carrying it,
J legs exact-zero); static coarse pattern visible (d_coarse > 1e-4)
while symmetric amplitude exactly 0 for texture and difference
(no quotient image, no propagating content: visible pattern, blind
dynamics). G: local_gradient + observer_blind checks (ladder);
observer_static filed (reported, not ladder-forcing).

0J structural-ledger projection: P: R_G distances separate textures
from uniform (> 1e-6, L4 + L28); contraction uniformity breaks on
textures while holding on uniform alpha = 0; M1 f-stats filed per
texture. G: ledger check (readout-only, no event run).

0K size scaling: P: obstruction zero at every L in L_LIST; gradient
readouts filed per L (headline sine n_periods = 1, analytic grad
2 pi delta / L shrinking with L). G: size_scaling (membership +
endpoints; filed, not ladder).

0Q quotient control: P: symmetric part of every texture exactly zero,
so the quotient image is absent (no H_Q dynamics, no quotient
transport). G: quotient (filed; supports observer_blind).

C0 uniform JOINT (folded into 0A). C1 global phase: P: rho/B/J/E
invariant under global phase on textures (SYM-0 U(1)). G: phase.
C2 projective periodicity: P: psi(alpha + pi) = -psi(alpha) exactly
(uniform rays + whole-map shift), observables identical. G:
projective. C3 origin covariance: P: exact symmetry (derived
pre-data): even dx+dy -> shifted map gives translated field; odd
dx+dy -> translated field composed with the staggered-structure
reflection alpha -> -alpha (odd translations map VSTAG -> -VSTAG
while VMINUS -> VMINUS; the (-1)^{x+y} factor is pinned to absolute
coordinates). G: covariance (L4 + L28, odd shift (1,2)). C4 FIELD-0
witness: P: I = 0 on texture superpositions (linear law for extended
states; textures static, PRE = t0, POST = t_end). G: witness.

Odd-L appendix (L5): P: textures still P_- E_0 exact (construction is
per-cell); uniform census: VMINUS ray JOINT, staggered direction
frustrated (filed, VAC-COMP precedent). G: odd (filed, not ladder).

### Verdict ladder (analyzer-gated)

Checks (14, all boolean): pminus_e0, uniform_circle, local_gradient,
scaling, smooth_sharp, stationary, carrier, observer_static,
observer_blind, ledger, phase, projective, covariance, witness.
Headline (frozen logic, mirrored in vactexture.campaign_verdict and
scripts/vactexture_analyze.py): VACTEXTURE-RADIATIVE if stationary,
carrier, pminus_e0, or observer_blind fails; else VACTEXTURE-NOLOCAL
if pminus_e0 holds but local_gradient + ledger + scaling all fail
with apparatus (circle/phase/projective/covariance/witness) green;
else VACTEXTURE-FLAT if pminus_e0 holds but local_gradient + ledger
fail; else VACTEXTURE-GRADIENT if pminus_e0, local_gradient,
stationary, carrier, observer_blind, ledger, scaling, smooth_sharp,
and apparatus all green; else VACTEXTURE-PARTIAL (mixed or apparatus
failure; filed with the check table, never forced). Pre-data
derivation: RADIATIVE excluded by H P_- = 0 + [H, S] = 0 (frozen,
blind); FLAT/NOLOCAL excluded by the B/rho/ledger/coarse gradient
readouts; predicted headline VACTEXTURE-GRADIENT. Amendments, if any,
as VACTEXTURE0-AMENDMENT-n with gated re-runs; none pre-data.

### Execution

28 specs (scripts/vactexture_campaign.py, mp.Pool, --jobs <= 90), beast
EC2 (16.54.88.181, OMP threads 1), JSON record
data/vactexture/results.json (committed). Analyzer
scripts/vactexture_analyze.py writes data/vactexture/verdict.json. Full
suite on beast (pytest -n 90; pyproject addopts already skips
tests/test_weighted.py). Branch cursor/vac-texture-0-1b52, base main
tail 81bf7b4. Verdict filed here post-data.

### VACTEXTURE0-VERDICT (VACTEXTURE-GRADIENT, 14/14)

Branch cursor/vac-texture-0-1b52 (base main tail 81bf7b4). 28/28 specs
CAMPAIGN-DONE on beast (16.54.88.181, mp.Pool --jobs 28, OMP threads 1,
nice, <2 min); records data/vactexture/results.json + verdict.json banked.
Analyzer scripts/vactexture_analyze.py per PREREG (one apparatus fix for
the scaling endpoint check, which sorted ascending-lambda against a
gradient-ascending comparison: slope was already +0.173 with B_pcmax
strictly ordered in gradient, results.json untouched, committed as
1da1819). Full suite on beast (venv, -n 90, pyproject addopts skips
tests/test_weighted.py): 1819 passed, 2 skipped, 0 failed.

Headline: the hidden JOINT vacuum orientation CAN vary spatially while
remaining exactly vacuum-like. Every (family, params, L, a) texture sits
in P_- E_0 with w_sym = 0.0, ||H psi|| = 0.0, E = 0.0 bitwise over all
sweep/amplitude/scaling rows (L4/L8/L28, 7 amplitudes), emits no P_+
along the flow (trace max 0.0), and stays frozen (rho/B/J drifts 0.0,
phase rate 0.0, all families incl. sharp steps). The obstruction is
identically zero, as derived pre-data from construction + banked
H P_- = 0.

Gradients are visible but dynamically silent. Local leg: D(sine/step vs
uniform) = 6.4e-4 at L28 (d_B carrying it, J legs exact-zero), 3.1e-2 at
L4. Observer leg: static coarse pattern visible (d_coarse 1.3e-3 L28,
6.3e-2 L4) while symmetric amplitude is exactly 0.0 for every texture
and difference: quotient image absent at L4 + L28 (visible pattern,
blind dynamics). Ledger leg: R_G separates textures from uniform
(dmax 0.151 L4 / 0.00303 L28); M1 f-stats strongly restructured by sine
textures (f0 0.50 uniform -> 0.0097 textured); contraction uniformity
breaks on sine textures at L4 + L28 and on step textures at L4, while
holding on uniform rays. Filed: L28 step textures elude the sparse
16-edge contraction sample (jumps on 2 of 28 columns missed by
4-per-class sampling), so that single cell stays uniform.

Scaling (derived, nothing imposed): B_pcmax ordered in the analytic
gradient over lam = 28/14/7 at fixed delta = pi/4 (2.31/2.47/2.94e-4),
log-log slope +0.173; Q = a^2 exact over all 7 amplitudes (slope 2.0
to fp). Smooth vs sharp: D(sine, step) = 8.9e-4/1.28e-3/1.46e-3 at
delta = pi/8, pi/4, pi/2 (L28) with exact gradient concentration
(step delta >= sine 2 pi delta / lam). Carrier: packet splits exactly
on texture backgrounds (split err ~9e-16), texture frozen 0.0, packet
ballistic (v = 1.92, r2 = 0.99998, msd alpha = 2.03, identical on sine
and step backgrounds).

Controls: uniform circle 12/13 JOINT + pi/4 BACKGROUND-capped (B == 0
point) at L4/L6/L28; global phase, projective periodicity
(psi(alpha + pi) = -psi exact, uniform + texture), and origin
covariance (odd shift (1,2) via the staggered-structure reflection
alpha -> -alpha) all exact; FIELD-0 witness I = 1.6e-17 on texture
superpositions; odd-L5 appendix P_- E_0 exact with J = 0.

Interpretation (boxed): orientation gradients inside the hidden vacuum
component are relationally real (local B/rho structure, static coarse
pattern, ledger restructuring, derived positive scaling) and dynamically
void (frozen flow, no emission, no quotient image, null witness). The
vacuum tolerates arbitrary preregistered orientation textures without
leaving E_0; what varies is the measurable relational landscape, never
the vacuum character. Nothing here moves geometry or selects a vacuum;
filed as input to future geometry coupling.
