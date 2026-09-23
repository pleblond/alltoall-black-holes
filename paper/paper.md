# Black Holes as Almost-Perfect All:All Entanglement Graphs

## Interior collapse, horizon wiring, and the micro-hole phase transition

**Draft v0.1 — computational companion paper**

> Source conversation: the author started from the intuition that black holes
> are "all:all entanglements" — from within, all nodes are next to all nodes —
> that a *perfect* all:all graph with zero exterior budget would pinch off as a
> baby universe, that horizon size counts *exterior* connections rather than
> interior bulk, and that a minuscule hole could stay ~zero-size until its
> exterior wiring forces an empty sphere into existence. This paper formalizes
> those three claims as Sections 1–3 and implements each as a runnable model in
> `src/bh_graph/`.

---

## Abstract

We study a toy model in which spacetime connectivity is an entanglement graph
and a black hole interior is an *almost-perfect* all:all (complete) subgraph.
Internal edges cost no exterior space; exterior legs ("wiring" to the ambient
graph) each cost ~ one Planck patch of horizon area. We show: **(1)** the
complete graph destroys interior distance (diameter 1, single-step operator
spread for any $N$) and reproduces the fast-scrambling hierarchy vs local
graphs; **(2)** horizon area scales as $A(k) = k\,l_p^2$ with exterior leg count
$k$, independent of interior node count $N$, with mass entering only through
the GR consistency condition $k \propto M^2$, and the $k \to 0$ limit is a
monogamy-forced pinch-off (baby universe); **(3)** micro-holes undergo a
horizon-formation phase transition — pointlike defects with $k\,l_p^2 <
4\pi r_{\mathrm{point}}^2$ that "pop" a horizon once the exterior budget exceeds
the point-embedding capacity, with an LQG-style minimal-area gap. The horizon
interior is, in this picture, mostly empty routing buffer. All claims ship with
reproducible simulations (`python scripts/generate_figures.py`) and an
interactive demo (`streamlit run app.py`).

---

## 1. All:all = no interior space (fast scrambling)

### 1.1 Setup

Let the interior be a graph $G_N$ on $N$Alternative nodes. We compare:

- **Complete** $K_N$: all:all, $|E| = N(N-1)/2$.
- **Chain** $P_N$: 1D-local baseline.
- **Grid** $\sqrt N \times \sqrt N$: 2D-local baseline.
- **Random 3-regular**: sparse expander baseline.

We track a deterministic SI / operator-spreading process: at $t=0$ one node is
"infected" (the infalling qubit's operator weight); each step, infected nodes
infect all graph neighbors. Cover time $t_{\mathrm{cover}}$ from the seed equals
the seed's eccentricity; worst case equals graph diameter.

### 1.2 Results (implemented in `bh_graph.scrambling`)

| family | diameter | $t_{\mathrm{cover}}$ scaling | mean distance | spectral gap |
|---|---|---|---|---|
| $K_N$ | **1** | **1 step, all $N$** | 1 | $N$ |
| chain | $N-1$ | $\sim N/2$ | $\sim N/3$ | $\sim \pi^2/N^2$ |
| grid | $\sim 2\sqrt N$ | $\sim 2\sqrt N$ | $\sim O(\sqrt N)$ | $\sim O(1/N)$ |
| random-regular | $\sim \log N$ | $\sim \log N$ | $\sim \log N$ | $O(1)$ |

![Fig 1](figures/fig1_scrambling.png)
![Fig 2](figures/fig2_graphs.png)

**Reading.** Only $K_N$ has diameter exactly 1 at every $N$: there is no "far
side of the hole." Something entering on the left is immediately adjacent to
everything that entered before — the qualitative content of Sekino–Susskind
fast scrambling ($t_* \sim \log N$ is the *slowest* a maximally nonlocal system
can be; our discrete SI toy saturates the stronger 1-step bound because it has
no Hamiltonian speed limit). In ER=EPR / Van Raamsdonk language, maximal
entanglement is zero-length connectivity, so the interior has no metric extent:
it is one dot.

Formally, run:

```bash
python -c "from bh_graph.scrambling import scrambling_scaling; print(scrambling_scaling([9,25,100]))"
```

---

## 2. Horizon size counts exterior wiring, not interior bulk

### 2.1 The area law

Decompose edges into $N(N-1)/2$ internal pairs and $k$ exterior legs to the
ambient graph, with $k \ll N^2$. Postulate:

$$A_{\mathrm{horizon}}(k) = k\,l_p^2, \qquad R(k) = \sqrt{k\,l_p^2/4\pi}.$$

$N$ drops out: adding interior nodes without adding exterior legs tightens
binding but buys no horizon area. Each exterior leg must be embedded through
the ambient geometry with Planck-density bandwidth, so $k$ legs need $k$ Planck
patches. This is the Bekenstein–Hawking / LQG puncture picture in graph
language (`bh_graph.horizon.horizon_area`, `horizon_radius`).

![Fig 3](figures/fig3_horizon_area.png)

### 2.2 Why mass grows the horizon

Purity + conservation force $k$ to track $M$. In Schwarzschild units ($G=c=1$):

$$k(M) = A/l_p^2 = 4\pi(2M)^2/l_p^2 \;\propto\; M^2,$$

implemented as `k_from_mass_schwarzschild`. Mass is, in this model, the Lagrange
multiplier enforcing the exterior budget: heavier means more entanglement that
*must* be spent outward.

### 2.3 Baby-universe pinch-off (monogamy)

Let $e_{\mathrm{int}} \in [0,1]$ be the interior entanglement fraction and
$e_{\mathrm{ext}}$ the exterior budget fraction. Monogamy imposes the frontier
$e_{\mathrm{int}} + e_{\mathrm{ext}} \le 1$ (toy-linear; `monogamy_frontier`).
At $e_{\mathrm{int}} \to 1$, $k \to 0$: maximal interior entanglement leaves no
budget for exterior entanglement, and the subgraph decouples — a closed graph,
i.e. a baby universe, no longer a black hole *in* our space. Black holes live
in the almost-perfect corner: $e_{\mathrm{int}} \lesssim 1$, small but nonzero
$k$.

![Fig 4](figures/fig4_monogamy.png)

---

## 3. Micro-holes: pointlike until they pop a horizon

### 3.1 Embedding capacity of a point

In 3D, a few legs ($k = 2,3,\dots$) radiate out of a point region of radius
$r_{\mathrm{point}}$ with no surface needed. They need a surface only when
Planck-density packing fails:

$$k\,l_p^2 < 4\pi r_{\mathrm{point}}^2 \;\Rightarrow\; \text{pointlike (particle)},$$

$$R_{\mathrm{obs}}(k) = \begin{cases} r_{\mathrm{point}} & k \le k_{\mathrm{crit}} \\ \sqrt{k\,l_p^2/4\pi} & k > k_{\mathrm{crit}} \end{cases}, \qquad k_{\mathrm{crit}} = 4\pi r_{\mathrm{point}}^2/l_p^2.$$

Implemented as `critical_k`, `is_pointlike`, `embedding_radius`. The interior of
the sphere is not "stuff" — it is empty routing gap inflated to give each leg
its own patch. The horizon *is* that routing surface.

### 3.2 Growth trajectory and area gap

Grow $N = 2,3,\dots$ with $k(N) = k_0 + \alpha N$ (`growth_trajectory`). Radius
stays flat at $r_{\mathrm{point}}$ and then pops — a genuine phase transition,
mirroring the appearance of a quantum extremal surface / entanglement island at
critical exterior entanglement. With an LQG-style gap $A_{\min}$
(`quantized_area`), area is $0$ below threshold and $\ge A_{\min}$ above: there
is no 0.2-Planck-area hole.

![Fig 5](figures/fig5_phase_transition.png)
![Fig 6](figures/fig6_quantized_area.png)

**Prediction.** Micro-holes are *not* scaled-down Schwarzschild holes. They are
point defects (indistinguishable from particles by size) until they cross a
critical entanglement budget, then acquire a horizon discontinuously in the
$N \to \infty$ / semiclassical limit.

---

## 4. Discussion

**Hawking evaporation** in this language is slow surgery on exterior legs: each
emitted quantum severs/rewires an exterior leg into an entangled pair shared
with radiation. The horizon shrinks because $k$ shrinks, not because interior
nodes are deleted. Page-time behavior maps to the exterior budget's
entanglement swapping from hole–ambient to radiation–ambient.

**What sets $k(N)$?** Standard GR says $k \propto M^2$, but the micro-mapping
$N \mapsto k$ is the open function of this model. Candidates: (a) random-tensor
averaging with fixed bond dimension; (b) a MaxEnt assignment under energy +
purity constraints; (c) an explicit bulk tensor network whose boundary bond
count is minimized. Falsifiable edge: any $k(N)$ sublinear enough to keep
astrophysical holes pointlike is ruled out; any super-quadratic $k(N)$ over
predicts horizon sizes.

**Limitations.** This is a graph-topology toy, not a derivation of GR. It has
no dynamics, no Hamiltonian, no Lorentz invariance, and the monogamy frontier
is linearized. Its value is intuition + scaling reproduction + a concrete
micro-hole prediction to test in fuller tensor-network / LQG / island
calculations.

---

## 5. Reproducibility

```bash
pip install -e .
python -m pytest tests/ -q
python scripts/generate_figures.py   # writes figures/fig*.png
streamlit run app.py                 # interactive Secs 1–3 explorer
```

Modules: `src/bh_graph/graphs.py`, `scrambling.py`, `horizon.py`, `micro.py`.

---

## References (starter set)

- Sekino & Susskind, *Fast Scramblers*, JHEP 2008.
- Van Raamsdonk, *Building up spacetime from quantum entanglement*, Gen. Rel. Grav. 2010.
- Maldacena & Susskind, *Cool horizons for entangled black holes*, Fortsch. Phys. 2013 (ER=EPR).
- Bekenstein, *Black holes and entropy*, Phys. Rev. D 1973; Hawking, *Particle creation by black holes*, 1975.
- Rovelli & Smolin, *Discreteness of area and volume in quantum gravity*, Nucl. Phys. B 1995.
- Penington / Almheiri et al., *Entanglement wedge reconstruction and the island formula*, JHEP 2019–2020.
- Hayden & Preskill, *Black holes as mirrors*, JHEP 2007.
