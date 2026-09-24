# Black Holes as Almost-Perfect All:All Entanglement Graphs — Explained

*A companion to the technical paper, written for scientifically literate
non-specialists: no physics degree assumed, but no hand-waving either.
Terms are introduced once, precisely, then used. For the full mathematics,
code, and tests, see `paper/paper.md`.*

---

## 0. Words we will use precisely

- **Node / edge.** The model treats reality at the smallest scale as a
  network: indivisible nodes joined by edges. You can picture atoms in a
  crystal, but the nodes here are far smaller (Planck scale, $10^{-35}$ m)
  and the "edges" are quantum entanglement — the measurable correlation
  between quantum systems, not metaphorical links.
- **All:all (complete) graph.** A network where every node connects directly
  to every other node. Distances inside it are trivial: one hop from anywhere
  to anywhere.
- **Exterior leg ($k$).** An edge crossing from a subgraph to the rest of
  the network. The model's central quantity: horizon area equals leg count
  times one Planck patch, $A = k\,l_p^2$.
- **Horizon.** In ordinary gravity, the surface of no return around a black
  hole. Here: the two-dimensional surface forced into existence when many
  exterior legs must be embedded in space without overlapping.
- **Scrambling.** How fast a localized disturbance spreads across all degrees
  of freedom of a system. Black holes are conjectured (Sekino–Susskind) to be
  the fastest scramblers allowed by quantum mechanics.

---

## 1. The thesis in one paragraph

Spacetime geometry is not fundamental; it is the large-scale appearance of
an entanglement network. A black hole interior is a subgraph wired
*almost* all:all — every node adjacent to every other — which destroys
interior distance: there is no far side inside. Its horizon size is set not
by how much is inside but by how many entanglement legs connect it to the
outside world, each costing roughly one Planck area. Perfect the internal
wiring (zero exterior legs) and the subgraph decouples entirely — a baby
universe. Shrink the leg count below a threshold and no horizon forms at
all: the object is pointlike until its exterior wiring exceeds what a point
can carry, at which point a horizon appears discontinuously.

## 2. Why distance can come from a network

Distance feels primitive, but condensed matter already shows otherwise:
sound cones, effective light speeds, and causal structure all *emerge* from
lattice couplings — no background geometry is put in by hand. The model
applies the same lesson to spacetime itself: define adjacency by
entanglement, and metric notions (near/far, area, and eventually curvature)
as large-scale statistics of the graph. This is the content of the ER = EPR
program (Maldacena–Susskind) and Van Raamsdonk's "spacetime from
entanglement": connectivity *is* geometry, viewed from outside.

Concretely: a regular lattice region of the graph looks, at scales far
above the spacing, like smooth flat space — signals propagate at a fixed
speed, areas scale as radius squared. Deviations appear only when the
wavelength approaches the spacing (tested in Appendix BD: quadratic
suppression, $10^8$ below Fermi bounds) or where the wiring is
inhomogeneous — which is what a horizon is.

## 3. All:all wiring, and why it kills interior distance

Compare two wirings of $N$ nodes. In a **local** graph (a grid: each node
linked to a few neighbors), a disturbance spreads step by step; crossing the
system takes $\sim \sqrt{N}$ steps, and "the other side" is meaningful. In
the **complete** graph $K_N$, every pair shares an edge: graph diameter is
exactly 1 at *any* $N$, and one infection step reaches everything. There is
no far side — not because the system is small, but because adjacency is
total.

The model identifies black-hole interiors with the second wiring (up to a
sparse exterior). The payoff is immediate: black holes are observed (in
theory: Sekino–Susskind; in principle on quantum hardware) to scramble
faster than any local system — operator spreading time $\sim \log N$ rather
than polynomial. Only effectively all:all interaction graphs do that. So the
model's first postulate isn't free decoration: it is *equivalent* to the
statement "black holes are the fastest scramblers," now geometrized. Our
simulations run the race explicitly — complete vs. chain vs. grid vs.
expander graphs — and only the complete graph collapses distance entirely
(Appendix A upgrades the toy to finite-speed random circuits and recovers
$t_* \sim \log N$ quantitatively).

## 4. Why horizons have size: exterior bandwidth, not interior bulk

The question the model answers most sharply: if the interior has no extent,
why do horizons come in sizes? Because **size counts exterior legs**.

Each leg joining the interior subgraph to the ambient graph must be embedded
through surrounding space, and space has finite bandwidth: at most one
elementary connection per Planck patch ($\sim l_p^2$). $k$ legs therefore
require $k$ patches — a surface of area $A = k\,l_p^2$, independent of the
interior node count $N$. The horizon is that surface: an *empty routing
buffer* inflated to host the wiring, containing (almost) nothing.

Two consequences worth pausing on. First, mass enters only indirectly:
consistency between the interior state and conservation laws forces heavier
holes to carry more exterior legs ($k \propto M^2$ in ordinary gravity), so
"massive $\Rightarrow$ large" survives, but as a *derived* statement about
wiring budgets, not bulk volume. Second, adding interior nodes without adding
legs changes nothing observable from outside — the interior can be arbitrarily
rich while the horizon stays fixed. (This decoupling is what makes the
information puzzle sharp, and its resolution possible; see §7.)

## 5. The perfectly wired limit: baby universes

Push the model to its endpoint: interior entanglement perfect, exterior legs
exactly zero. Monogamy of entanglement — a theorem, not an assumption: a
system maximally entangled internally has no entanglement left to share
externally — forces the subgraph to decouple completely. It no longer
interacts with, curves, or is located in our space. It is a closed graph: a
baby universe, causally cut off.

Black holes in this picture live *near* but not *at* that limit: $N(N-1)/2$
internal edges, $k \ll N^2$ exterior legs. The "almost" in the title is doing
real work — it is the precise amount by which a black hole fails to be a
separate universe, and everything observable (area, temperature, radiation)
lives in that failure.

## 6. Micro-holes: pointlike until they pop

Now run the logic downward. A handful of nodes, all mutually linked, with a
few exterior legs: in three dimensions, a few outgoing connections radiate
from a point with no surface needed — the object is pointlike, particle-like,
with no horizon in any operational sense.

Grow the leg count. At a critical value $k_{crit} = 4\pi r_{point}^2/l_p^2$,
the legs can no longer share a point without exceeding Planck packing
density, and geometry must inflate a routing surface. A horizon appears —
not by growing continuously from zero, but discontinuously, as a phase
transition (with a minimum-area gap analogous to loop quantum gravity's area
spectrum: area $0$, then $\ge$ one quantum, nothing between).

So micro black holes are *not* scaled-down Schwarzschild holes in this
picture. They are a distinct phase — point defects — until a sharp
entanglement-budget threshold promotes them. This mirrors, in full quantum
gravity language, the sudden appearance of quantum extremal surfaces
("islands") in entanglement calculations: below threshold the outside's
entanglement wedge contains no interior at all.

## 7. Evaporation and information, briefly

Each Hawking quantum severs roughly one exterior leg and carries its
entanglement into the ambient graph as radiation. The horizon shrinks because
$k$ shrinks — interior nodes are never "deleted." Crucially, the exterior
budget's entanglement is gradually *swapped* from hole–ambient to
radiation–ambient, which reproduces the Page curve (radiation entropy rising
then falling, turning over halfway). Information is never inside waiting to
escape; it was always being re-encoded into the wiring, and the wiring leaves
leg by leg. The baby-universe endpoint inherits nothing because, by the time
$k \to 0$, there is nothing left to inherit — the no-cloning constraint is
satisfied by evacuation ordering, checked explicitly in the paper.

## 8. How this could be proven wrong

A model that can't die isn't science. Ours carries pre-registered,
quantitative falsifiers (Appendix AN):

1. **Scrambling hierarchy (lab).** The same spreading protocol on grid-wired
   vs. all:all-wired qubit arrays (trapped ions already offer all:all
   hardware): we predict the all:all time shorter by a factor $\approx
   2$–$3\times$ at 36+ qubits. A measured ratio below $1.3$ kills it.
2. **Ringdown damping (LIGO/Virgo/KAGRA).** We identify horizon relaxation
   with ringdown, fixing the damping coefficient $\alpha = 11.24$ (no
   freedom). Per-event deviations outside $[9.0, 12.4]$ in future catalogs
   kill it.
3. **Collider thermality (LHC).** Sub-critical objects are pointlike and
   non-thermal; thermal onset sits near $\sim 550$ TeV for TeV-scale gravity
   benchmarks. Any thermal-shaped excess with a soft tail where we predict
   pointlike behavior kills Section 3.
4. **Leg entanglement density (theory).** Horizon formation needs
   $s_{leg} > l_p^2/4$ per exterior leg. Any physical black-hole-like state
   class violating it restricts or kills the threshold mechanism (closest
   call so far: critical Ising at $2.2\times$ clearance).
5. **Tensor-network area law.** If any serious tensor-network calculation
   finds boundary entropy tracking bulk size $N$ rather than boundary legs
   $k$, the core $A(k)$ postulate fails.
6. **Vacuum dispersion (astrophysics).** Discrete legs forbid *linear*
   light-speed shifts exactly (a lattice symmetry); any confirmed linear
   Lorentz-violation signal kills the discrete-leg picture outright.

One sub-claim has already died this way (Planck-mass remnant dark matter,
ruled out by abundance arithmetic plus published bounds — kept on record
with a narrow surviving window at $\sim 4\times10^5$ g).

## 9. What this model is not

- **Not a quantum gravity theory.** It reproduces large parts of gravity
  (Newton's law, Kepler orbits, GPS and Pound–Rebka redshifts, first-order
  light bending, ringdown damping) from network postulates plus explicitly
  labeled borrowed principles (equipartition, the equivalence principle,
  continuum limits). Deriving Einstein's equations from nothing is not
  claimed; three partial routes toward the Einstein–Hilbert action are shown
  with their bridge assumptions named.
- **Not a phenomenology of the sky.** At astrophysical scales it is general
  relativity by construction, so it predicts *nulls* (achromatic lensing,
  standard EBL opacity, no echoes above $\sim 10^{-160}$) rather than
  anomalies. Its testable frontier is the laboratory (item 1) and precision
  gravitational-wave catalogs (item 2).
- **Not an explanation of any standing anomaly.** Several candidates were
  examined (fast radio bursts, lensing oddities, TeV transparency, remnant
  dark matter); each died on arithmetic, on the record. What survives is a
  coherent, falsifiable toy — not a solution in search of a problem.
- **Missing pieces, named:** the spatial-curvature sector ($g_{rr}$ —
  Mercury precession is a clean miss at $0$ vs $43''$/cy), the exact gap
  coefficient, a formation story for delocalized giants, and unitary
  leg-surgery dynamics (evaporation is currently a Markov chain on $k$).

## 10. Where to go next

- **The paper proper:** `paper/paper.md` (readable draft, Secs 1–3 +
  appendices) and `paper/main.pdf` (compiled LaTeX) — same narrative, every
  claim with equations, derivations, and honesty-labeled assumptions.
- **See it run:** `streamlit run app.py` opens an interactive explorer:
  scrambling races across graph families, horizon growth leg by leg,
  evaporation, Page curves, and every appendix with sliders.
- **Check the homework:** `python -m pytest tests/ -q` runs 240+ checks
  (every numbered claim in the paper has at least one); `python
  scripts/generate_figures.py` regenerates all figures from code.
- **Cite it:** see `CITATION.cff` (DOI via Zenodo in `README.md`).

---

*Index-card version: interiors are all:all (no interior distance); horizons
count exterior legs (bulk drops out of size); perfect wiring pinches off
(baby universes); small holes stay pointlike until wiring congestion forces a
bubble (micro-hole pop). Everything else is working out what those four
sentences imply — and trying, hard, to break them.*
