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

