# Black Holes as Almost-Perfect All:All Entanglement Graphs — Explained

*A companion to the technical paper, written for educated non-physicists who
already know what quantum entanglement is. Everything else is defined as
needed; the mathematics is kept to a handful of formulas, each translated.
For the full derivations, code, and tests, see `paper/paper.md`.*

---

## 0. Words we will use precisely

- **Node / edge.** The model treats reality at the smallest scale as a
  network of indivisible nodes joined by edges, where an edge *is* a unit
  of entanglement (think Bell pairs as the atomic bond) and the edge count
  across any cut sets an upper bound on the entanglement entropy across it.
  Nodes live at the Planck scale ($10^{-35}$ m).
- **All:all (complete) graph.** A network where every node connects directly
  to every other node. Distances inside it are trivial: one hop from anywhere
  to anywhere.
- **Exterior leg ($k$).** An edge crossing from a subgraph to the rest of
  the network. The model's central quantity: horizon area equals leg count
  times one Planck patch, $A = k\,l_p^2$.
- **Horizon.** In ordinary gravity, the surface of no return around a black
  hole. Here: the two-dimensional surface forced into existence when many
  exterior legs must be embedded in space without overlapping.
- **Scrambling.** How fast a localized operator spreads over all degrees of
  freedom, as diagnosed by out-of-time-order correlators (OTOCs): black holes
  are conjectured (Sekino–Susskind) to saturate the bound $t_* \sim \log N$,
  faster than any locally-interacting system allows.

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

## 4. How things move: walks on the network

Everything in the model moves the same way: **one edge per tick.** A
disturbance — a particle, a signal, an operator — is a walker hopping from
node to node along edges. On a regular lattice region this produces
ordinary straight-line motion on average: the walker jitters left and right
but its mean position advances steadily, exactly like a drunkard who drifts
downhill. Macroscopic trajectories, light cones, and causal structure are
just what edge-hopping looks like from far above.

Crucially, **different frequencies walk differently.** A wave of wavelength
$\lambda$ accumulates phase as it goes, and every edge it crosses imprints a
phase error proportional to how many of its own oscillations fit across
that edge — roughly $a/\lambda$ per edge, where $a$ is the spacing. A
long-wavelength (low-energy) wave barely notices the grain: millions of
wavelengths average thousands of edges each, and it sails through as if
space were smooth. A short-wavelength (high-energy) wave samples every
defect: its many rapid oscillations multiply each edge's jitter, scattering
it and slowing its group velocity. In equations the lattice gives group
velocity $v_g \approx c(1 - (ka)^2/8)$ — quadratic in energy, tested in
Appendix BD — and our wave simulations show transmission loss growing
$\propto \omega^2$ with frequency (Appendix BF). Same geometry, different
walks: radio light sees glass where TeV light sees frost.

## 5. Gravity from legs: Newton to Mercury, tested

Walks plus congestion turn out to be *gravity*. The chain of reasoning is
short enough to state in full. Screens around a mass count legs ($k \propto
r^2$); spreading the mass-energy evenly over those legs defines a
temperature falling as $1/r^2$; moving a small mass outward changes
entropy linearly with distance (Bekenstein's bound); and force is
temperature times entropy gradient. Multiply through: $F = M_1M_2/r^2$ —
**Newton's law**, with $G = 1$ in Planck units, verified in code to a
log-log slope of exactly $-2$. Feed that force to an orbit integrator and
Kepler's third law ($T^2 \propto r^3$) drops out downstream.

The same machinery reaches further. The Newtonian potential plus the
equivalence principle gives gravitational redshift with no new parameters —
and out come textbook digits: GPS clocks fast by $+5.3\times10^{-10}$,
Pound–Rebka $2.5\times10^{-15}$ over 22.5 m. Near a horizon, congestion
slows fronts ($c_{eff} \to 0$), freezing escape in the tortoise-like way
general relativity predicts. And light bending through the congestion field
gives the full $4M/b$ — *not* the half-strength value a naive
equivalence-principle argument yields (we predicted the failure, ran the
calculation, and lost the bet on the record). Shapiro delay follows from
the same integral and matches Cassini.

The last gap — Mercury's orbit — closed when we derived the
spatial-curvature sector ($g_{rr}$) from leg tortuosity: radial rulers
stretch as $(1+x/2)^2$ through the packed legs, giving $\gamma = 1$
exactly and Mercury's $43''$/century by direct orbit integration
(42.99" measured, identical to general relativity at this precision).
So the scoreboard reads: Newton ✓, Kepler ✓, redshift ✓, bending ✓,
Shapiro ✓, Mercury ✓ — weak-field gravity complete to first
post-Newtonian order. The honest boundary now sits one order higher:
second-order predictions (e.g. light bending's $c_1 = 3.36$ vs GR's
$1.94$) differ, are currently untestable, and are pre-registered as a
forward falsifier rather than hidden.

## 6. Why horizons have size: exterior bandwidth, not interior bulk

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
information puzzle sharp, and its resolution possible; see §9.)

To put the point bluntly: **the inside contributes nothing to the size; the
outside contributes everything.** Think of a building whose size is set by
its doors — one door-width per entrance, doors that cannot overlap — while
the interior rooms (TARDIS-like) can be few or infinite without moving a
single outer wall. Here the "doors" are exterior legs, the "door width" is
one Planck patch, and the unbreakable rule is that *outside space is
uncompressible*: patches cannot overlap, bandwidth cannot be exceeded. The
horizon is outside space's response to wiring congestion — never a measure
of interior contents.

## 7. The perfectly wired limit: baby universes

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

## 8. Micro-holes: pointlike until they pop

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

Why, then, does such an object have *no size at all* while plainly
existing? Because in this model **existence and size are different
properties.** Existence means *being connected*: $k > 0$ legs joining our
graph, through which the object interacts, scatters, gravitates. Size means
*needing a surface*: legs so numerous through one region that space must
inflate to host them. Below $k_{crit}$ there is connection without
congestion — presence without extent. Everyday objects bundle the two
together (to exist is to occupy space); the model splits them apart, and
the micro-hole phase is where the split shows.

## 9. Evaporation, disappearance, and the fate of information

A black hole evaporates the way a rope bridge comes apart: **exterior legs
snap one by one, and each snap emits something.** Each severed leg's
entanglement leaves into the ambient graph as one quantum of Hawking
radiation. The horizon shrinks because the *count* of outside connections
shrinks — interior nodes are never "deleted." Follow this to the end: the
last legs go, $k \to 0$, and the interior pinches off. It is not destroyed;
it is *disconnected* — no longer interacting with, curving, or located in
our space. From our side, the black hole has disappeared from the universe,
leaving only the radiation it emitted along the way.

What happens to the *information* — everything that ever fell in? Two
endings are possible, and the model characterizes exactly what decides
between them:

- **Preserved (the fiducial outcome).** Each cut leg carries up to $s_{leg}$
  bits out; total capacity over the hole's life is $k_0 \cdot s_{leg}$ against
  interior content $S_0$. Since derived leg budgets scale as $k^* \sim N^2$
  while content scales as $S_0 \sim N$, capacity wins by a factor $\sim N$:
  everything drains before pinch-off, the baby is born empty, and the
radiation purifies along the Page curve (entropy rising, turning over
halfway, falling). No cloning occurs, because at the moment of pinch-off
there is nothing left inside to clone.
- **Lost from our universe (Hawking's 1976 position, made precise).** If
  evaporation ever outruns evacuation — information still inside when the
  last legs go — pinch-off strands it outside our spacetime: genuinely,
  permanently lost *to us* (whether a baby universe inherits it is then
  unobservable by construction). The paper flags exactly this condition as
  "cloning risk": the race is capacity vs. content, and loss is what losing
  the race means.

Which ending is real? Within the model as built, evacuation wins by a large
margin — but the loss branch is not philosophy; it is a computed threshold
away, and the paper keeps it visible rather than assuming it away. (A
subtler version of the race — information *flux* vs. per-leg channel
capacity in the final non-adiabatic moments — is saved for future work;
see the open problems in §11.)

## 10. How this could be proven wrong

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

## 11. What this model is not

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
- **Missing pieces, named:** the micro-derivation of tortuosity's
  $\sqrt{\chi}$-linearity (the load-bearing assumption behind $g_{rr}$ and
  Mercury), the exact gap coefficient, a formation story for delocalized
  giants, unitary leg-surgery dynamics (evaporation is currently a Markov
  chain on $k$), and the information-flux race in the final non-adiabatic
  moments (per-leg channel capacity vs. required evacuation flux).

## 12. Where to go next

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
