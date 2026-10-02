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
