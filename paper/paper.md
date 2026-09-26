# Black Holes as Almost-Perfect All:All Entanglement Graphs: Interior Collapse, Horizon Wiring, and the Micro-Hole Phase Transition

**Philippe Leblond** — leblond.philippe@gmail.com

**Draft v3.12-BV — computational companion paper (Secs 1–3 + Appendices A–BS, BV)

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
graph) each cost ~ $4\ln 2 \approx 2.77$ Planck patches of horizon area (derived, BS). We show: **(1)** the
complete graph destroys interior distance (diameter 1, single-step operator
spread for any $N$) and reproduces the fast-scrambling hierarchy vs local
graphs; **(2)** horizon area scales as $A(k) = 4\ln 2\cdot k\,l_p^2$ with exterior leg count
$k$, independent of interior node count $N$, with mass entering only through
the GR consistency condition $k \propto M^2$, and the $k \to 0$ limit is a
monogamy-forced pinch-off (baby universe); **(3)** micro-holes undergo a
horizon-formation phase transition — pointlike defects with $4\ln 2\cdot k\,l_p^2 <
4\pi r_{\mathrm{point}}^2$ that "pop" a horizon once the exterior budget exceeds
the point-embedding capacity, with an LQG-style minimal-area gap. The horizon
interior is, in this picture, mostly empty routing buffer. Beyond Secs 1–3,
the appendices derive weak-field gravity to first post-Newtonian order from
the same leg network: Newton's law, Kepler's laws, textbook redshift digits,
full-strength light bending, Cassini-grade Shapiro delay, $\gamma = 1$
exactly, and Mercury's $43''$/cy by direct geodesic integration. Attraction's
sign is derived from pure flux with zero tuning (negative radial
Ollivier-Ricci in every configuration). At weak field, we further study gravity
as an emergent consequence of graph transport and exterior entanglement
capacity: microscopic lattice walks alone do not reproduce the Newtonian
inverse-square law, while their combination with the model's exterior-leg
thermodynamic structure yields the $1/r^2$ force law; an independent
Ollivier–Ricci analysis finds the expected negative radial curvature sign,
although its quantitative scaling remains an open problem. In the UV
($\chi \to 1$), tortuosity is derived as line-defect scattering with
entanglement cost $\ln 2$ per encounter ($c \approx 0.44$–$0.60$ with zero
tuning, predicting $p = 2c$ and $\gamma = 2c$), and the horizon pop appears
as graph disconnection at $k_{crit} = 4\pi r^2/\sigma$ with no metric input
(BV). All claims ship with
reproducible simulations (`python scripts/generate_figures.py`) and an
interactive demo (`streamlit run app.py`).

---

## Results at a glance

| sector | headline | status |
|---|---|---|
| gravity | Newton, Kepler, redshift, bending, Shapiro, Mercury 42.99" | all pass (AS, AT, AU, BB, BH) |
| quantum info | scrambling hierarchy, Page curve, QES pop, Hayden–Preskill | derived (A, C, F, H) |
| phenomenology | no LHC thermal BHs, no echoes, achromatic lensing | nulls held (T, AN5, BB) |
| open frontier | 2nd-PN $c_1 = 3.36$ vs GR $1.94$; tortuosity $1/2$ derived (BV), $\mu(\chi)$ still assumed | pre-registered (AN wire 6, BH→BV) |

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

![Fig 1](../figures/fig1_scrambling.png)
![Fig 2](../figures/fig2_graphs.png)

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

$$A_{\mathrm{horizon}}(k) = 4\ln 2\cdot k\,l_p^2, \qquad R(k) = \sqrt{4\ln 2\cdot k\,l_p^2/4\pi}.$$

$N$ drops out: adding interior nodes without adding exterior legs tightens
binding but buys no horizon area. Each exterior leg must be embedded through
the ambient geometry with Planck-density bandwidth, so $k$ legs need $k$ Planck
patches. This is the Bekenstein–Hawking / LQG puncture picture in graph
language (`bh_graph.horizon.horizon_area`, `horizon_radius`).

![Fig 3](../figures/fig3_horizon_area.png)

### 2.2 Why mass grows the horizon

Purity + conservation force $k$ to track $M$. In Schwarzschild units ($G=c=1$):

$$k(M) = A/4\ln 2\,l_p^2 = (4\pi/\ln 2)M^2/l_p^2 \;\propto\; M^2,$$

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

![Fig 4](../figures/fig4_monogamy.png)

---

## 3. Micro-holes: pointlike until they pop a horizon

### 3.1 Embedding capacity of a point

In 3D, a few legs ($k = 2,3,\dots$) radiate out of a point region of radius
$r_{\mathrm{point}}$ with no surface needed. They need a surface only when
Planck-density packing fails:

$$4\ln 2\cdot k\,l_p^2 < 4\pi r_{\mathrm{point}}^2 \;\Rightarrow\; \text{pointlike (particle)},$$

$$R_{\mathrm{obs}}(k) = \begin{cases} r_{\mathrm{point}} & k \le k_{\mathrm{crit}} \\ \sqrt{4\ln 2\cdot k\,l_p^2/4\pi} & k > k_{\mathrm{crit}} \end{cases}, \qquad k_{\mathrm{crit}} = 4\pi r_{\mathrm{point}}^2/4\ln 2\,l_p^2.$$

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

![Fig 5](../figures/fig5_phase_transition.png)
![Fig 6](../figures/fig6_quantized_area.png)

**Prediction.** Micro-holes are *not* scaled-down Schwarzschild holes. They are
point defects (indistinguishable from particles by size) until they cross a
critical entanglement budget, then acquire a horizon discontinuously in the
$N \to \infty$ / semiclassical limit.

---

## 4. Discussion

**Hawking evaporation** in this language is slow surgery on exterior legs (see
Appendix D for the implemented Page curve): each emitted quantum severs/rewires
an exterior leg into an entangled pair shared with radiation. The horizon
shrinks because $k$ shrinks, not because interior nodes are deleted. Page-time
behavior maps to the exterior budget's entanglement swapping from hole–ambient
to radiation–ambient.

**What sets $k(N)$?** Appendix B constrains it instead of postulating it:
MaxEnt counting gives the linear capacity bound $k \ge N s_{node}/s_{leg}$,
and gravitational self-consistency ($R = \sqrt{4\ln 2\cdot k l_p^2/4\pi} = 2E$,
$E = \varepsilon N$) fixes the fixed point
$k^*(N) = 16\pi(\varepsilon N/l_p)^2/4\ln 2$ — given $R = 2E$ as input (the
circle enters here; BM localizes it, it is not derived). The remaining free number is the
per-node energy $\varepsilon$, not a free function (BS update: $\varepsilon$
runs as $c/\sqrt{N}$, so $k^* \propto N$ and $\alpha = k^*/N = 1$ exactly;
linear $\alpha$ growth holds only for the fixed-$\varepsilon$ matching form).

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

Modules: `src/bh_graph/graphs.py`, `scrambling.py`, `horizon.py`, `micro.py`,
`circuits.py` (A), `maxent.py` (B), `qes.py` (C), `evaporation.py` (D),
`qec.py` (F), `robustness.py` (G), `kerr.py` (H), `haar.py` (I), `monogamy.py` (J), `otoc.py` + `pheno.py` (L), `tn.py` (M), `kerrpage.py` (N), `syk.py` (O), `data.py` (Q), `litcompare.py` (R), `tev.py` (T), `echoes.py` (U), `posteriors.py` (W), `ds.py` (X), `krylov.py` (Y), `collapse.py` (AA), `cosmic.py` (AB), `lunch.py` + `remnant.py` (AC), `bounds.py` (AE), `healing.py` (AG), `mss.py` (AH), `bigsyk.py` (AI), `mp.py` + `greybody.py` (AJ), `congestion.py` (AK), `charge.py` (AL), `bandwidth.py` (AM), `gridcirc.py` + `monitor.py` + `selfattack.py` + `lhc.py` (AN), `concentration.py` (AO), `ps.py` (AP), `scatter.py` (AQ), `emd.py` + `viability.py` (AR), `entropic.py` (AS), `redshift.py` (AT), `heatker.py` + `orici.py` + `jacobson.py` (AU), `fission.py` (AV), `klanguage.py` (AW), `tension.py` (AX), `gw250114.py` (AY),
`overtones.py` + `tensionvol.py` (AZ), `sparse24.py` (BA), `lensing.py` +
`chroma.py` + `shapiro.py` (BB), `bcrit.py` (BC), `dispersion.py` (BD),
`qnmfoot.py` + `qnmlegs.py` (BE), `foamgrid.py` (BF), `perwalk.py` (BG).

---

## Appendix A. Finite-speed circuits: deriving $t_* \sim \log N$

Sec 1's 1-step SI toy assumed infinite parallelism (every infected node infects
*all* neighbors per step). Appendix A (`bh_graph.circuits`) imposes the physical
constraint of one 2-qubit interaction per qubit per step. Pairings are a random
perfect matching (all:all) vs a random dimer covering (chain); infection crosses
an active pairing with probability $p$.

Early growth on all:all is exponential (each infected qubit meets a fresh
susceptible partner with high probability), giving
$t_*(N) \approx \log_2 N / \log_2(1+p)$ — exactly $\log_2 N$ at $p = 1$ —
while the chain spreads ballistically, $t_* \sim N/v(p)$. Measured over 25
trials per $N$, $N = 8 \dots 128$: all:all fits the log law (straight line on
log-linear axes), chain grows linearly and is already >5× slower at $N = 64$.

![Fig 7](../figures/fig7_circuit_scrambling.png)

This promotes Sec 1 from "consistent with fast scrambling" to "derives the
Sekino–Susskind $\log N$ bound from the model's own dynamics."

## Appendix B. Deriving $k(N)$: MaxEnt bound + gravitational fixed point

(`bh_graph.maxent`.) Step 1 — information capacity: interior entropy
$S_{int} \sim N s_{node}$ must fit the exterior budget $S_{ext} \sim k s_{leg}$,
so $k \ge N s_{node}/s_{leg}$ (linear lower bound, no gravity assumed; the
random-tensor calculation $S_{ext} = \min(N\log d, k\log D)$ shows the same
bottleneck structure). Step 2 — self-consistency: the budget sets its own radius
$R = \sqrt{4\ln 2\cdot k l_p^2/4\pi}$, and a self-gravitating mass $E = \varepsilon N$
demands $R = 2E$ ($G = c = 1$). Solving gives the fixed point (fixed-$\varepsilon$ form)

$$k^*(N) = 16\pi(\varepsilon N/l_p)^2/4\ln 2 \propto N^2,$$

stable under damped iteration from any start. The free *function* $k(N)$ is
gone; one free *number* $\varepsilon$ remains at matching scale (BS: runs as
$c/\sqrt{N}$). Falsifiable corollary (BS-revised): $\alpha(N) = k^*/N = 1$
exactly under running $\varepsilon$ — legs match nodes one-to-one.

![Fig 8](../figures/fig8_k_of_n.png)
![Fig 8b](../figures/fig8b_alpha_of_n.png)
![Fig 8c](../figures/fig8c_tensor_bottleneck.png)

## Appendix C. QES pop from generalized-entropy crossing

(`bh_graph.qes`.) The Sec 3 "pop" is now a computed crossing, not an input
threshold shape. Candidates: $S_{no}(k) = k s_{leg}$ (naive Hawking, grows
forever) vs $S_{isl}(k) = k\ln 2\,l_p^2 + \max(S_0 - k s_{leg}, 0)$ (area + remaining
bulk). If twice bulk entropy per leg exceeds area cost per leg ($s_{leg} > \ln 2\,l_p^2/2$,
now an explicit falsifiable assumption), they cross at
$k_{page} = S_0/(2s_{leg} - \ln 2\,l_p^2)$: below it the minimal surface is trivial
(pointlike, no island), above it the island/QES dominates. An explicit
core+legs flow network reproduces the same turnover in its min-cut value.

![Fig 9](../figures/fig9_qes.png)

Failure mode is sharp: if $s_{leg} \le l_p^2/4$ there is *no* crossing and Sec 3
dies — the model would predict pointlike objects at all scales.

## Appendix D. Page curve from leg surgery

(`bh_graph.evaporation`.) Each step severs one exterior leg ($k \to k-1$) and
emits one entangled pair; radiation entropy follows Page,
$S_{rad}(t) = \min(t, N_{eff}-t)$ bits, turning over at $t = N_{eff}/2$.
Crucially, area evolution is *identical* whether $N$ shrinks with $k$ (standard)
or $N$ stays fixed (wiring-only): $A(t)$ tracks $k(t)$ alone. The horizon
shrinks because the exterior budget is spent, not because interior nodes are
deleted — the distinctive Sec 2 claim, now demonstrated rather than asserted.

![Fig 10](../figures/fig10_page.png)

---

## References (starter set)

- Sekino & Susskind, *Fast Scramblers*, JHEP 2008.
- Van Raamsdonk, *Building up spacetime from quantum entanglement*, Gen. Rel. Grav. 2010.
- Maldacena & Susskind, *Cool horizons for entangled black holes*, Fortsch. Phys. 2013 (ER=EPR).
- Bekenstein, *Black holes and entropy*, Phys. Rev. D 1973; Hawking, *Particle creation by black holes*, 1975.
- Rovelli & Smolin, *Discreteness of area and volume in quantum gravity*, Nucl. Phys. B 1995.
- Penington / Almheiri et al., *Entanglement wedge reconstruction and the island formula*, JHEP 2019–2020.
- Hayden & Preskill, *Black holes as mirrors*, JHEP 2007.

## Appendix F. QEC check: Hayden-Preskill mirror vs exterior budget

(`bh_graph.qec`.) Recovery error for a diary qubit under Haar-random all:all
dynamics obeys $err(k) = \min(1/2, 2^{N/2+1-k})$: guessing ($F = 1/2$) below
$k \sim N/2$, then exponential climb to a mirror ($F \to 1$ a few legs past
half). The 99%-fidelity threshold is $k \ge N/2 + 1 + \log_2 100$. In the
baby-universe limit $k \to 0$ the diary is sealed off — exactly the decoupling
Sec 2 demands. The model's QEC story is therefore self-consistent: almost-all:all
+ budget = fast mirror; perfect all:all = no outside recovery.

## Appendix G. Robustness: the results are not fine-tuned

(`bh_graph.robustness`, Fig 11.) (i) Circuit log law persists at every gate
success $p$, slope $1/\log_2(1+p)$ — noisy gates only steepen it. (ii) $k^*(N)$
is exactly quadratic ($k^*(2N)/k^*(N) = 4$) for every $\varepsilon$; only the
coefficient $16\pi(\varepsilon/l_p)^2$ moves. (iii) The QES boundary is sharp:
transition iff $s_{leg} > l_p^2/4$. So A–C each survive parameter sweeps with
their failure modes made explicit rather than hidden.

![Fig 11](../figures/fig11_qec_robust.png)

## Appendix H. Kerr-Newman: spin and charge as wiring budgets

(`bh_graph.kerr`, Fig 12.) With $r_+ = M + \sqrt{M^2-a^2-Q^2}$ and
$A = 4\pi(r_+^2+a^2)$, effective legs $k_{eff} = A/l_p^2$ fall monotonically
with spin at fixed $M$: extremal Kerr ($a = M$) keeps exactly half the
Schwarzschild legs; extremal Reissner-Nordstrom a quarter. Rotation *orders*
legs (correlates them), charge soaks them into flux — the area law
$A = 4\ln 2\cdot k_{eff} l_p^2$ survives with $N$ still absent. Spin budget
$1 - A(M,a)/A(M,0) \to 1/2$ is now a second, independent exterior budget the
model must track; a Kerr Page curve with spin-dependent $k_{eff}(t)$ is the
natural next calculation.

![Fig 12](../figures/fig12_kerr.png)

## Appendix I. Exact Page curve with Haar-typical fluctuations

(`bh_graph.haar`, Fig 13.) Page's exact $S(m,n) = H(mn) - H(n) - (m-1)/2n$
replaces the $\min()$ idealization: the curve dips $\sim 1/2$ nat ($\approx
0.72$ bits) below naive at turnover — information starts leaking just *before*
the naive Page time. Direct Haar sampling ($N = 8$, 30 states per $t$) tracks
the mean with small spread: the Page curve is typical, not fine-tuned, and
leg-surgery evaporation inherits that typicality.

![Fig 13](../figures/fig13_haar_page.png)

## Appendix J. Nonlinear monogamy from explicit states

(`bh_graph.monogamy`, Fig 14.) On
$|\psi(t)\rangle = \cos t\,|\Phi^+\rangle|0\rangle + \sin t\,|00\rangle|1\rangle$,
Wootters $C^2_{AB}$ vs exterior one-tangle $\tau_{E|AB}$ traces a frontier
strictly below the linear toy ($x + y = 0.70$ at $t = 0.3$), from the
baby-universe point $(1, 0)$ around to product $(0, 0)$. CKW deficit
$\tau_{A|BE} - C^2_{AB} - C^2_{AE} \ge 0$ verified on a 25-point grid. The
linear $e_{int} + e_{ext} \le 1$ is therefore a *conservative outer bound*:
real states pinch off sooner, which only strengthens the baby-universe limit.

![Fig 14](../figures/fig14_monogamy.png)

## Appendix L. OTOC Lyapunov toy + phenomenology signposts

(`bh_graph.otoc`, `bh_graph.pheno`, Fig 15.) Early OTOC growth
$C(t) \sim e^{\lambda t}/N$ on all:all gives $t^* = \log N/\lambda$
(MSS-style; fitted $\lambda$ recovers the input to $< 0.1$), vs ballistic
$t^* = N/v$ on chains — the same hierarchy as Appendices A and 1, now in chaos
language. Phenomenology, honestly order-of-magnitude: PBHs evaporating today
sit at $\sim 10^{18}$--$10^{19}$ Planck masses ($\sim 10^{14}$ g); sub-critical
(pointlike) holes would evaporate *without* greybody horizon suppression; GW
echo spacing in wiring language reads $\Delta t \sim M\log k$. The nearest-term
empirical handle remains analogue: all:all vs local scrambling is directly
comparable on programmable trapped-ion / superconducting processors.

![Fig 15](../figures/fig15_otoc.png)

## Appendix M. Tensor network derives $\varepsilon$

(`bh_graph.tn`, Fig 16.) A central Gaussian random tensor with $N$ bulk legs
($d = 2$) and $k$ boundary legs ($D = 2$), traced over the bulk, reproduces
the Hayden et al.\ min-rule $S_{bdy} = \min(N\log d, k\log D)$ numerically
($N = 4$, $k = 1\ldots8$, 10 trials). Minimal wiring follows:
$k_{min} = S_{bulk}/\log D$. The per-node energy $\varepsilon$ — the last free
number from Appendix B — is then fixed two ways that must agree: (a) QES
coincidence $\varepsilon = (l_p/N)\sqrt{4\ln 2\cdot k_{page}/16\pi}$ with
$k_{page} = S_0/(2s_{leg} - \ln 2\,l_p^2)$; (b) linear-quadratic crossover
$\varepsilon = l_p\sqrt{4\ln 2\cdot s_{node}/(16\pi\log D\,N_{match})}$. E.g.\ $D = 2$,
$s_{node} = \log 2$, $N_{match} = 25$ gives $\varepsilon \approx 0.047\,l_p^{-1}$.
$\varepsilon$ is no longer an input: it is tensor-network data plus one
crossover scale (BS: runs as $c/\sqrt{N}$ — M gives $\varepsilon(25)$).

![Fig 16](../figures/fig16_tn.png)

## Appendix N. Kerr Page curve: spin lowers and delays

(`bh_graph.kerrpage`, Fig 17.) With $M(t) = M_0(1-t/T)^{1/3}$ and faster
spin-down $J(t) = J_0(1-t/T)^{1.2}$, $S_{phys} = \min(g(S_0 - S_{BH}), S_{BH})$,
$g = 1.48$: $a_0 = 0.95$ peaks at 65% of the Schwarzschild peak and turns over
at $t/T = 0.73$ vs $0.54$. The delay is physical, not a bug: shedding $J$ at
fixed $M$ *grows* area, offsetting early mass-loss shrinkage. Initial
speculation said "earlier"; the numerics corrected it — spin is a second
exterior budget with its own Page phenomenology.

![Fig 17](../figures/fig17_kerrpage.png)

## Appendix O. SYK exact diagonalization vs local chain

(`bh_graph.syk`, Fig 18.) $N = 6, 8, 10$ Majorana SYK (Jordan-Wigner,
Gaussian $J_{ijkl}$, $\mathrm{var} = 6J^2/N^3$, dim $\le 32$) vs mixed-field
Ising chains on identical Hilbert spaces, infinite-$T$ OTOC for distant $X$
operators: SYK reaches $C = 0.4$ first at $n_q \ge 4$, and $t^*$ stays flat
($\approx 1.1$--$1.5$) while the chain's grows linearly ($1.1 \to 2.5$ over
3--5 qubits) — the log-vs-linear signature at the smallest sizes ED allows.
Majorana Clifford algebra and Hermiticity verified; MSS $\lambda \le 2\pi T$
saturation at low $T$ is cited (Maldacena-Stanford), not reproduced:
infinite-$T$ ED tests the hierarchy, which is what the model claims.

![Fig 18](../figures/fig18_syk.png)

## Appendix Q. Repurposed public data: GWTC mergers create legs

(`bh_graph.data`, Fig 19.) Live LIGO-Virgo-KAGRA catalog medians via the GWOSC
event API (32 BBH events, GWTC-3-confident; bundled literature fallback
offline): mapping $k = (4\pi/\ln 2) M^2/l_p^2$ (BS flip) with $M_\odot \approx 9.14\times10^{37}
m_P$, **every** merger satisfies $k_f > k_1 + k_2$ — median fractional creation
$0.77$ at median radiated fraction $0.04$. The Hawking area theorem in wiring
language: mergers are leg-creation events; radiated mass is more than paid for
by the nonlinear $k \propto M^2$ law. Spin neglected (Schwarzschild areas), but
remnant $a_f \sim 0.7$ costs only $\sim 13\%$ of the final area vs $\sim 77\%$
median margin — the conclusion cannot flip. This is the model's first contact
with real astrophysical data, and it passes.

![Fig 19](../figures/fig19_gwtc.png)

## Appendix R. Quantum hardware: literature consistency + head-to-head prediction

(`bh_graph.litcompare`, Fig 20.) Published anchors: Garttner et al.\ 2017
(100+ Penning-trap ions, all:all Ising) built $m$-body OTOC coherences up to
$m = 8$ — rapid multi-body spread on all:all wiring, as Sec 1/A predict; Mi et
al.\ 2021 (Sycamore 53q, local grid) saw ballistic average-OTOC decay with
classically-simulable spreading — local behavior, as predicted. Different
protocols, so consistency only — but the controlled test is now sharply posed:
same OTOC protocol at $N = 53$ should find $t^* \approx 7.9 \pm 0.7$ steps on
all:all (trapped-ion) wiring vs $\approx 14.6$ on grid (superconducting), ratio
$\approx 1.9\times$ ($9.9\times$ vs a 1D chain). A null result (no separation)
would falsify the Sec 1/A hierarchy at the hardware level.

![Fig 20](../figures/fig20_headtohead.png)

## Appendix S. Anomalies: what this model can and cannot say

Honest ledger. **GW "echoes"** (contested Abedi et al.\ claims): the wiring
language gives $\Delta t \sim M\log k$ (Appendix L), so *if* echoes were ever
confirmed, the model has a natural slot for them — but it does not predict
their amplitude, and current evidence is weak; no claim made. **LHC micro-BH
null results** (13 TeV, thermal channels): expected, not surprising, under Sec
3 — sub-critical holes are pointlike and non-thermal, so thermal-channel
non-observation is compatible at any $k_{crit}$ above the LHC reach; this
recasts a null as consistent rather than explaining an anomaly. **PBH bounds**
(microlensing, Fermi-LAT, CMB): unaffected — constrained PBHs sit far above
$k_{crit}$; only the final Planck-time of evaporation differs (no greybody
suppression), which is unobservable. **EHT shadows, X-ray spins, mass gaps,
Hubble tension, $g-2$, etc.**: no connection; the model is GR-identical at
astrophysical scales by construction. Net: the model *survives* all current
public data (Appendix Q positively) but *explains* no standing anomaly — its
testable frontier is analogue/lab (Appendix R), not the sky.

## Appendix T. TeV gravity: LHC thermal nulls recast as expected

(`bh_graph.tev`, Fig 21.) With $M_D = 1$ TeV ($l_D \approx 2\times10^{-19}$ m),
Myers-Perry masses across the LHC reach sit at $k \approx 11$ ($3$ TeV) to $17$
($13$ TeV) for $n = 6$ — a factor $\sim 3$--$5$ *below* $k_{crit} \approx 50$
($r_{point} = 2l_D$), and pointlike across $M_D = 1$--$5$ TeV. Sub-critical
holes are non-thermal point defects (Sec 3), so ATLAS/CMS thermal-channel
non-observations (high-multiplicity democratic decays) are *compatible at any
$k_{crit}$ above LHC reach* — the null is recast from "no micro BHs" to "no
*thermal* micro BHs, as the pointlike regime expects." Falsifier preserved: a
thermal-spectrum excess at $k < k_{crit}$ would break Sec 3.

![Fig 21](../figures/fig21_tev.png)

## Appendix U. Echo timescales land in searched windows (amplitude-free)

(`bh_graph.echoes`, Fig 22.) $dt = 4M\log(M/l_p)$ gives $0.03$--$0.3$ s across
bundled remnants (GW150914: $0.11$ s) — inside the $O(0.01$--$1)$ s windows
echo searches covered. LVK nulls therefore bound *reflectivity*, which the toy
does not predict: compatible, not confirmed. The wiring form $dt \sim M\log k$
makes the scaling testable in principle: echoes far from $M\log k$ would count
against the picture; echoes tracking it (with amplitude from a future
reflectivity calculation) would count for it.

## Appendix V. EHT bound + wormhole anchor

(`bh_graph.pheno`, `bh_graph.litcompare`.) Planck-scale microstructure shifts
shadow sizes by $\sim l_p/2M \approx 10^{-48}$ (M87*) — $47$ orders of
magnitude below EHT $O(10\%)$ precision (Fig 22, right): quantitative proof the
model is GR-identical in the sky, and a quantitative no-go for EHT tests.
Fourth literature anchor: Jafferis et al.\ 2022 (Sycamore 9q learned sparse
SYK-like model, teleportation/"wormhole" signal) — teleportation is the
Hayden-Preskill mirror primitive of Appendix F, and the signal surviving on a
*sparse* all:all graph supports the "almost-perfect suffices" thesis of Sec 2.

![Fig 22](../figures/fig22_echo.png)

## Appendix W. Spin-aware leg creation from GW150914 posteriors

(`bh_graph.posteriors`, Fig 23.) GWOSC GWTC-1 Overall_posterior (8350
samples): per-sample Kerr component areas from aligned spins
$\chi_z$, source masses via Planck15 $d_L \to z$ inversion, remnant from
$M_f = 63.1 \pm 1.5\,M_\odot$, $a_f = 0.68 \pm 0.06$ Gaussians. **$P(\Delta
k > 0) = 100\%$** with median fractional creation $0.57$ (vs $0.77$
Schwarzschild-medians: the spin correction is quantified, not hand-waved).
Every posterior sample sits above the area bound in the initial-vs-final
legs plane. This is the Appendix Q result with spins on both ends.

![Fig 23](../figures/fig23_posterior.png)

## Appendix X. The cosmic horizon owns the universe's wiring budget

(`bh_graph.ds`, Fig 24.) Planck15 gives $\Lambda \approx 2.9\times10^{-122}$,
$S_{dS} = 3\pi/\Lambda \approx 3\times10^{122}$, $k_{dS} = 4S \approx
10^{123}$ legs wiring our static patch to the beyond. All stellar black
holes ($\sim 10^{101}$) plus all SMBHs ($\sim 10^{101}$) are $20+$ orders of
magnitude below — black holes are wiring rounding error next to $\Lambda$.
The Nariai radius $1/\sqrt{\Lambda} \approx 10^{26}$ m marks where the two
budgets merge. Baby-universe reading extends: a closed slicing has no
exterior at all.

![Fig 24](../figures/fig24_cosmic.png)

## Appendix Y. Krylov hierarchy: saturation, not slope

(`bh_graph.krylov`, Fig 25.) Spread complexity from Lanczos chains (full
reorthogonalization, dim 16): SYK saturates at $\approx 2\times$ the chain's
spread ($\approx 3.5$ vs $1.9$) with a higher late plateau — it explores far
more Krylov space. Notably, early-slope and peak-time order the *opposite*
way for a computational-basis start (transverse field rattles fast but
locally), so those metrics were demoted and saturation promoted — an honest
correction recorded in code and tests. The Sec 1 hierarchy holds in Krylov
language at the level that is actually robust.

![Fig 25](../figures/fig25_krylov.png)

## Appendix AA. Collapse is a scrambling/code transition

(`bh_graph.collapse`, Fig 26.) Grid + long-range edges with $p = c^6$,
compactness $c \in [0, 1]$: diameter $10 \to 1$ in a $0.55$-wide window,
spectral gap switches on, and 40%-erasure LCC diameter collapses to $1$ —
any surviving subset stays a clique. Forming a horizon = becoming a fast
scrambler = becoming an optimal erasure code, all at once. Sharpness tracks
$\gamma$ (stated, not hidden: $\gamma = 6$ fiducial sharp, $3$ gradual);
GR motivates sharp since horizons form suddenly. Direct consequence that
distinguishes black holes from matter *within* the model, and suggests an
analogue test: quench a simulator's connectivity and watch $t^*$ jump.

![Fig 26](../figures/fig26_collapse.png)

## Appendix AB. Cosmic legs open up; the patch is unscrambled

(`bh_graph.cosmic`, Fig 27.) $\Lambda$CDM event-horizon legs grow
$10^{122.3}$ ($1$ Gyr) $\to 10^{123.1}$ (late dS): the early universe is a
nearly-closed baby-like patch gaining its exterior with time (an initial
"focusing from infinity" guess was wrong — the dS future converges the
integral from any $t$ — and corrected). dS scrambling time
$t^* = H^{-1}\log S_{dS} \approx 4000$ Gyr $\approx 300\times$ the cosmic age:
super-horizon correlations must be primordial, never dynamically generated.

![Fig 27](../figures/fig27_cosmic.png)

## Appendix AC. Lunch grows as the horizon shrinks; remnants fail DM

**Erratum (v1.8, see Appendix AR):** remnant abundance corrected (growth + EMD branch); failure now localized to $M \gtrsim 10^6$ g and $M \lesssim 10^5$ g with a narrow viable window at $\sim 4\times10^5$ g.

(`bh_graph.lunch`, `bh_graph.remnant`, Fig 28.) With $C(t) = C_0 + vt$ and
wiring-only $k(t)$: lunch $C/k$ diverges through evaporation — the interior
keeps getting harder to decode while looking smaller outside (Python's lunch
with size replaced by complexity). Remnants: each evaporated PBH leaves
$M_P$, but required $\beta \propto M^{5/2}$ exceeds unity above $\sim 10^6$
g — BBN-era masses fail decisively, ultralight needs literature bound curves
not encoded here. A direct consequence that mostly *fails*: kept as a
negative result constraining the baby-universe end-state story.

![Fig 28](../figures/fig28_lunch.png)

## Appendix AE. Remnant DM vs published bounds: excluded, decisively

**Erratum (v1.8, see Appendix AR):** the required-beta formula used here omitted PBH-fraction growth; the verdict stands but the numbers are superseded by the corrected viability map.

(`bh_graph.bounds`, Fig 29.) Vendored PBHbounds evaporation curves (Kavanagh;
EGRB, Voyager, INTEGRAL, SuperK, CMBevap, 511keV, Comptel) converted
$f_{PBH} \to \beta(M)$ from first principles
($\beta = f(\Omega_{DM}/\Omega_{rad})(T_0/T_{form})$, $\gamma = 0.2$).
Two independent kills: (i) required $\beta > 1$ (unphysical) for all
$M \gtrsim 10^6$ g — no data needed; (ii) where photon bounds cover
($5\times10^{14}$–$10^{17}$ g), required exceeds them by $40+$ orders of
magnitude — $10^6\times$ beyond any conceivable $\gamma/g^*/$convention
systematic. Remnant DM survives only, if at all, for ultralight PBHs against
induced-GW bounds not encoded here. The AC negative result is now a
data-backed exclusion, and the baby-universe end-state must shed remnants as
a DM candidate (closed nuggets can still exist — they just cannot be the
dark matter).

![Fig 29](../figures/fig29_bounds.png)

## Appendix AF. Single-device quench protocol (sharpened head-to-head)

No new module: numbers from Appendices AA + A. On a tunable-coupler device
(Sycamore-class), quench the *same* $6\times6$ patch from grid to all:all
connectivity mid-scrambling-run. Predicted jumps (SI cover / diameter):
$t^*$ $8 \to 1$ steps, diameter $10 \to 1$, spectral gap $0.27 \to 36$ —
with the crossover concentrated in a $0.55$-wide compactness window
($\gamma = 6$). This removes Appendix R's cross-platform systematics (ions
vs superconducting, different gates): same qubits, same protocol, wiring as
the only knob. A null (no $t^*$ jump) falsifies the collapse-transition
picture directly; a jump with the predicted sharpness promotes AA from toy
to lab-observed transition.

## Appendix AG. Healing is not instant: ringdown is the lag

(`bh_graph.healing`, Fig 30.) $dA/dt = (4\ln 2\cdot k l_p^2 - A)/\tau_{heal}$ with the
timescale fixed by data: identifying the merger step response with ringdown
gives $\tau_{heal} = 1/\mathrm{Im}(\omega_{220}) = 11.24\,M$ — $3.5$ ms for
GW150914's remnant, the measured damping scale. Two-sided pinch-off follows:
the baby side keeps a closed $N$-node graph (causally cut off — nothing
"comes out" here, the ADM mass already radiated); our side heals leftover
buffer, trivially for pointlike holes (clean vanish) and exponentially for
ex-horizon ones (a $\le$ Planck-energy sigh, fraction $\sim 10^{-78}$).
Slow evaporation tracks adiabatically; mergers and the final Planck moments
go non-adiabatic. Timescale ladder at $63\,M_\odot$: healing $3.5$ ms,
scrambling $0.23$ s ($66\times$), Page $10^{79}$ s, evaporation $10^{80}$ s —
separate rungs, separate physics, all computed.

![Fig 30](../figures/fig30_healing.png)

## Appendix AH. MSS tested (finite-size) + randomness qualifier + $\alpha$ bounds

(`bh_graph.mss`, Fig 31.) Regularized thermal OTOC on $N = 10$ SYK:
$\lambda/2\pi T = 0.50$ ($\beta = 0.5$) rising to $0.68$ ($\beta = 1$) —
bound respected with the saturation *direction* visible; low-$T$ fits freeze
out at dim $32$ (stated limit, needs large-$N$ Krylov work). Uniform-all:all
LMG control scrambles strictly worse (lower max, later threshold): with
Tran et al.\ 2020 and DHS 2023 (uniform all:all has power-law, not log,
saturation time), the model's slogan is now qualified in code and text —
*random/chaotic* all:all scrambles fast; mere density does not. Healing
coefficient from GWTC-3 hierarchical $\delta\tau_{220} \in [-0.2, +0.1]$
(Abbott et al.\ 2021): $\alpha \in [9.0, 12.4]$ at 90% — the AG prediction
$11.24$ sits inside with $\sim 20\%$ headroom each side. New anchors:
Landsman 2019 (tunable-range ions: longer range, faster OTOCs — direct
hierarchy support) and Seki 2025 (Quantinuum H1 has all:all connectivity but
ran a local circuit and noted all:all $\to O(\log N)$ — the AF quench is one
firmware change away on that exact device).

![Fig 31](../figures/fig31_mss.png)

## Appendix AI. Big SYK: clean separation to 10 qubits, MSS headroom stable

(`bh_graph.bigsyk`, Fig 32.) Sparse Pauli-string SYK to $N = 20$ (dim 1024)
with typicality+Krylov OTOCs (validated: sparse==dense Hamiltonians, 0.95
correlation with exact OTOC at $N = 8$): $t^*$ flat at $\approx 1.0$--$1.3$
for SYK across 4--10 qubits while the chain climbs $1.8 \to 6.2$ — the
log-vs-linear hierarchy with no finite-size ambiguity left. Thermal MSS at
$N = 16$: $\lambda/2\pi T = 0.41, 0.66$ ($\beta = 0.5, 1$), stable vs $N = 10$;
$\beta = 2$ fits $1.03$ — at the bound within fit systematics at dim 256,
reported as "consistent modulo systematics," not a violation claim (MSS is a
large-$N$ statement; the honest next step is sparse-Lanczos $N \ge 24$).

![Fig 32](../figures/fig32_bigscaling.png)

## Appendix AJ. Haar-typical TN spectrum + greybody switch

(`bh_graph.mp`, `bh_graph.greybody`, Fig 33.) Star-tensor boundary spectra
match Marchenko-Pastur moments and support (variance within 30% at tiny
dims, density normalized): the Appendix M entanglement is genuinely
Haar-typical — a faked (diagonal-mixture) state could match the entropy but
never MP. Square-barrier transmission $T(E)$ is analytic: horizon present
$\to$ low-$\omega$ suppression with total-emission ratio $< 1$; pointlike
($k < k_{crit}$) $\to$ barrier gone $\to$ $T \equiv 1$. This grounds Appendix
T's load-bearing assertion (sub-critical holes emit unsuppressed) in one
formula, and predicts the thermal/non-thermal emission transition tracks
$k_{crit}$ rather than any fixed mass scale.

![Fig 33](../figures/fig33_mp_grey.png)

## Appendix AK. Horizons are congestion: footprint-dependent $k_{crit}$

(`bh_graph.congestion`, Fig 34.) Repairing Sec 3's hidden assumption (all legs
from one point): with footprint $r_{foot}$, congestion
$\chi = 4\ln 2\cdot k l_p^2/4\pi r_{foot}^2$ decides — bubble iff $\chi > 1$, $R_b =
\sqrt{k l_p^2/4\pi}$. Concentrated legs recover $k_{crit} = 4\pi
r_{src}^2/l_p^2$ exactly; spread legs never bubble at any $k$ — a giant
interior with $k = 10^6$ legs over $r_{foot} = 10^6 l_p$ sits deep in the
delocalized phase (multi-mouth ER network, volume nowhere). Three phases:
baby ($k = 0$), delocalized ($\chi \le 1$), horizon ($\chi > 1$). The 1-leg
object is pinpoint by the same token: one leg congests nothing.

![Fig 34](../figures/fig34_congestion.png)

## Appendix AL. Charge pins legs: evaporation endpoints

(`bh_graph.charge`, Fig 35.) $q = 4\pi Q^2/l_p^2$ legs protected by Gauss's
law; $k(t) = \max(k_0 - t, q)$. Neutral: full pinch-off, nothing left here.
Small charge ($Q = 0.5$): pointlike remnant, $M \sim 0.42\,M_P$, stable in our
space. Large charge ($Q = 5$): extremal remnant BH. Extremality $A \ge 4\pi
Q^2$ verified along every trajectory. Charged holes cannot fully disconnect;
neutral ones must. (Schwinger discharge neglected: valid for small cold
charges; stated caveat.)

![Fig 35](../figures/fig35_charge.png)

## Appendix AM. Last-leg bandwidth: babies born empty, divergence = risk

(`bh_graph.bandwidth`, Fig 36.) $S_0$ bits drain at $s_{leg}$ per cut;
fiducial $k^* \sim N^2$ vs $S_0 \sim N$ evacuates with $\sim N\times$ margin —
pinch-off with vacuum inside, no cloning. Adversarial ($s_{leg}$ tiny):
leftover at $k = 0$ flags "cloning risk," forbidding the last cut until more
flows — the dynamical content of "why would it disconnect." Corrected in
testing: info-per-leg diverges $\iff$ risk (clean cases drain to 0); the
naive "last legs carry the most, always" was wrong and is now the diagnostic.

![Fig 36](../figures/fig36_bandwidth.png)

## Appendix AN. Pre-registered kill list (six live wires)

One appendix, six executable falsifiers — thresholds fixed *before* the data:

1. **AF quench** (`gridcirc`, Fig 37). Same-device grid$\to$all:all quench at
$N \ge 36$: predicted $t^*_{grid}/t^*_{all} \approx 2$--$3\times$ (simulated
$2.09, 2.40, 3.00$ at $N = 16, 36, 64$). **KILL if ratio $< 1.3$**; confirm in
$[1.3, 5]$; above $5$ is device anomaly, not confirmation.
2. **$\alpha$ universality** (`monitor`). Combined kill if hierarchical
$\delta\tau_{220}$ excludes $0$ at 90% (now $[-0.2, +0.1]$: alive);
universality kill if per-event $\alpha_i$ scatter with $\chi^2$ $p < 0.01$ or
trends with mass. Scaffold runs today on synthetic rows, awaits O4/O5 rows —
reports "awaiting data," never a free pass.
3. **Min-rule self-attack** (`selfattack`, Fig 38). Violations $15\% \to
2\%$ shrinking with $N$ (attack fails — Page corrections fade as theory
says). Would-be kill (violations growing with $N$) not observed.
4. **$s_{leg}$ probe** (`selfattack`, Fig 38). Random TN $s_{leg} \approx
0.69$, critical Ising GS $0.55$ vs bound $\ln 2/2 \approx 0.347$ (BS flip) —
QES assumption holds with Ising as narrowest clearance ($1.6\times$). A
physical state class under $0.347$ would restrict Appendix C's domain
(noted, not found).
5. **LHC thermal shape** (`lhc`, Fig 39). Onset masses $\gg$ LHC reach at all
benchmarks ($\sim 600$ TeV at $M_D = 1$ TeV, $n = 6$); pre-registered hard
spectra with no soft tail below onset. **KILL on any thermal-shaped excess
with a soft tail where $k(M) < k_{crit}$.**
6. **Second-order bending** (`lensing`, BH). First-PN light bending matches
GR exactly, but the second-order coefficient is pre-registered at $c_1 =
3.36$ vs GR's $1.94$ — currently untestable by $\sim 6$ orders. **KILL the
strong-field extrapolation on any future measurement consistent with GR's
$1.94$ and excluding $3.36$ at 90%.**

![Fig 37](../figures/fig37_quench.png)
![Fig 38](../figures/fig38_selfattack.png)
![Fig 39](../figures/fig39_lhc.png)

## Appendix AO. Big pops from hidden giants (LRD-adjacent scenario)

(`bh_graph.concentration`, Fig 40.) The pop radius $R_b = \sqrt{k l_p^2/4\pi}$
is set by pre-existing $k$, not by the trigger: a delocalized $k \sim 10^{97}$
giant (Appendix AK: gravitating, horizonless, dark) that concentrates pops a
$\sim 10^8\,M_\odot$ horizon when $\chi$ crosses 1 — analytically
$t_{pop} = t_{ff}(1 - (R_b/r_0)^{3/2})$. Fiducial: $10^8\,M_\odot$ over
$100$ pc free-falls to a pop in $\sim 2$ Myr vs $\sim 600$ Myr Eddington
growth from $100\,M_\odot$ ($\sim 300\times$ faster — the mass is
pre-assembled and hidden, so no luminous accretion is needed). Stated
homework: no metric for delocalized objects (assumed diffuse $\sim$ halo),
no formation story (primordial wiring fluctuations?), no CMB/lensing
constraint pass on $10^7$–$10^9\,M_\odot$ diffuse clumps at $z > 7$, and the
LRD anomaly itself is softening toward AGN interpretations. Scenario sketch
with a working trigger and honest gaps — not a claimed solution.

![Fig 40](../figures/fig40_bigpop.png)

## Appendix AP. Structure check: halos suffice, monsters excluded

(`bh_graph.ps`, Fig 41.) Press-Schechter with exact $\Lambda$CDM growth
($D(8) = 0.14$) and $\sigma(M,z)$ anchored to $M_*$ today
($\gamma = 0.16$, band $[0.12, 0.22]$): demand $10^{-5}\,\mathrm{Mpc}^{-3}$
needs $\sim 0.1\%$ occupation of $>10^{10}\,M_\odot$ halos at $z = 8$
(survives across the whole band — `structure_kills` False), $\sim 100\%$ of
$>10^{11}\,M_\odot$ (implausible but unexcluded), and exceeds $>10^{12}$
supply everywhere (constrained out). Verdict: hidden giants must live in
garden-variety high-$z$ halos, not rare monsters — a derived constraint, and
the AO scenario survives structure. Caveat: if giants are primordial and
halo-independent, this check is inapplicable and CMB/lensing bounds (not
computed) take over.

![Fig 41](../figures/fig41_ps.png)

## Appendix AQ. Overmassive-tail prediction vs wiring fraction

(`bh_graph.scatter`, Fig 42.) Mock high-$z$ $M_{BH}$–$M_*$: baseline
$\log M_{BH} = \log M_* - 3 \pm 0.3$ plus wiring channel (fraction $f_w$,
host-independent $\log M_{BH} \sim U(6, 9)$). Tail $P(M_{BH}/M_* > 0.1)$
rises $0 \to 0.58$ over $f_w \in [0, 1]$; a $10\%$ UHZ1-like tail maps to
$f_w \approx 0.18$. Pre-registered kill: zero outliers in $300$ complete
systems forces $f_w < 0.017$ (rule-of-three at 95%), killing the channel's
relevance (not the core model); $30$ clean systems cannot kill it. Direction
(one-sided overmassive tail, no undermassive counterpart) is the robust
prediction; amplitude awaits selection-corrected JWST samples.

![Fig 42](../figures/fig42_scatter.png)

## Appendix AR. Obituary and resurrection: remnants, corrected

(`bh_graph.emd`, `bh_graph.viability`, Fig 29 rewritten.) **Erratum first:**
Appendices AC/AE omitted the PBH fraction's growth ($\propto a$) between
formation and evaporation — wrong by $\sim 9$ orders at $10^{10}$ g. The
corrected RD abundance $\Omega h^2 = \beta(M_P/M)(T_{form}/T_{eq})0.143$ and
its EMD branch ($\beta$-independent, continuous at $\beta_{dom} = 1/57M$)
redraw the map as max-achievable $\Omega(M) \propto M^{-2.5}$:

- $M \gtrsim 10^6$ g: max $\ll 0.12$ — **dead** (the AE verdict stands, now
for the right reason; photon bounds pile on where they cover).
- $M \sim 4\times10^5$ g: max $\approx 0.12$ — **viable sweet spot**,
$\sim 0.4$ dex wide, any $\beta \gtrsim 10^{-12}$ (EMD), evaporating at
$10^{-9}$ s ($T_{RH} \sim 10$ GeV, BBN-safe), no current photon/poltergeist
coverage. Resurrected, narrowly.
- $M \lesssim 10^5$ g: max $\gg 0.12$ — **excluded** (overclose-or-negligible,
no middle ground).

Open checks on the window (flagged): current $\Delta N_{eff}$ integral vs the
poltergeist spectrum needs Inomata et al.'s calculation (beyond toy scope),
and formation at $\beta \gg 10^{-12}$ needs an inflationary mechanism.
Future poltergeist-GW probes (sensitive to $\beta \gtrsim 10^{-5}$–$10^{-8}$
at $10^3$–$10^5$ g) are the scheduled executioner-or-confirmer. The death
stands corrected and dated; the resurrection is conditional and narrow —
exactly as it should be.

![Fig 29](../figures/fig29_bounds.png)

## Appendix AS. Entropic Newton: $F = M_1M_2/r^2$ from leg capacity

(`bh_graph.entropic`, Fig 43.) Verlinde's chain with screens made concrete:
$k(r) = 4\pi r^2/4\ln 2\,l_p^2$ legs (Sec 2, BS) $\to$ equipartition over Planck bits $T = 2M_1/k(r)4\ln 2$
$\to$ Bekenstein $dS = 2\pi M_2\,dr$ $\to$ $F = T\,dS/dr = M_1M_2/r^2$
($G = 1$), verified to log-log slope $-2$ within $10^{-9}$, potential/force
consistent, leapfrog orbits closing with $T^2 \propto r^3$. The subtlety that
kills naive attempts is implemented alongside: raw link-flux also scales
$N_1N_2/r^2$, but as an *energy* that would give $1/r^3$ — the temperature
factor (same energy over a growing screen) corrects it to $1/r^2$. Model
contribution vs borrowed postulates, stated plainly: (i) is ours (legs as
screen bits, $k(N)$ derived); (ii)–(iv) are Verlinde's, translated. Newton
from all:all topology holds to exactly the extent those postulates do.

![Fig 43](../figures/fig43_newton.png)

## Appendix AT. Redshift: derived weak-field, modeled near-horizon

(`bh_graph.redshift`, Fig 44.) Part 1 is a derivation: Appendix AS's
$\Phi = -M/r$ plus weak-field $g_{00} = 1 + 2\Phi$ plus equivalence gives
$z = M(1/r_1 - 1/r_2)$ with no new parameters — GPS $+5.29\times10^{-10}$
and Pound-Rebka $2.55\times10^{-15}$ reproduced to textbook precision.
Part 2 is a model: layered graph with stay profile $s(r) = (R_s/r)^\alpha$
(tangential wandering from congestion) slows SI fronts to $c_{eff} = 1 -
s(r) \to 0$ at the horizon with tortoise-divergent escape ($R^2 > 0.99$ vs
$-\log(r - r_h)$); $\alpha = 1$ matches Schwarzschild $dr/dt$ exactly
(calibration), $\alpha = 2$ is the naive angular-size guess (qualitative).
Ledger: redshift itself is robust to the profile; the exact exponent is open
leg-termination microphysics — the same class of unknown as the gap
coefficient, and the honest price of the near-horizon claim.

![Fig 44](../figures/fig44_redshift.png)

## Appendix AU. Three routes to Einstein-Hilbert (bridges labeled)

Heat kernel (`heatker`), Ollivier-Ricci (`orici`), Jacobson chain
(`jacobson`), Fig 45. (1) Torus Laplacian spectra: spectral dimension
$2.05$, $a_0 = 11.9$ vs $N/4\pi = 11.5$, and $a_1$ shifting $+16.2 \to
-4.0$ under a conformal bump — the curvature response read relatively
(flat-lattice $a_1 \ne 0$ artifact stated; continuum $a_1 \to \int R$
cited). (2) Ollivier $\kappa$: line $0$, tree $< 0$, $K_6 > 0$ (all
exact signs), $S = \sum_e \kappa(e) = 0$ on flat grids — curvature native
to topology, converging to Ricci on geometric graphs per Ollivier's
theorems (cited). (3) Clausius across a leg-cut fixes $\varepsilon =
\kappa/8\pi$ with $G = 1/4\eta = 1$ — Einstein's equations follow given
Raychaudhuri for leg bundles (open; Appendix AT's congestion slowdown is
the seed). Three independent convergences on $\int R\sqrt{-g}$; a full
derivation from nothing is not claimed — each bridge is named.

![Fig 45](../figures/fig45_eh.png)

## Appendix AV. Fission done right: $K_N^2$, corrected mapping, no "traversable"

(`bh_graph.fission`, Fig 46.) One $K_N$ interior, two disjoint footprints:
a non-traversable multi-boundary ER microstate (shared interior, no GJW
coupling — the "traversable" label refused). Budget $k = k_1+k_2+\Delta
k_{rad}$ ($\Delta k_{rad} \ge 0$ always); no-split rule $k < 2k_{crit}$;
cross-links $(N/2)^2$ uncut (cutting them is $O(N^2)$ baby pinch-off, not
fission). Corrected mapping, tested: saturation $k_f = k_1+k_2 \iff 29\%$
radiated (equal mass), no-loss $k_f = (\sqrt{k_1}+\sqrt{k_2})^2 \iff E_{rad}
= 0$ — the thread's inversion repaired and locked by test.

![Fig 46](../figures/fig46_fission.png)

## Appendix AW. k-language audit: one mass map

(`bh_graph.klanguage`.) $M(k) = l_p\sqrt{k}/4\sqrt{\pi}$ as the single source
of truth, with $E_{rad}$, $\eta_A$, and both landmark limits re-derived from
it and cross-checked against the horizon/data/remnant/LHC/healing modules to
machine precision. GW150914-like point ($k_f/(k_1+k_2) \approx 1.8$) lands at
$\sim 5\%$ radiated. Any future bound in mass units passes through here.

## Appendix AX. Mouth tension: parametrized, bounded, not set

(`bh_graph.tension`, Fig 46.) $E(d) = \sigma(d/l_p)^p$ postulated openly
(new physics, labeled as such — legs have no length-energy in the current
model); $F = -dE/dd$ computed; thermal activation $\Gamma \sim e^{-E/T_H}$
inverted into $\sigma$ floors from fission non-observation. The thread's
$\sqrt{k}$ assertion is superseded: barrier shape follows from $(\sigma, p)$,
to be pinched by data (or derived from complexity growth — flagged as the
research-grade alternative).

## Appendix AY. GW250114 medians + SYK-24 anchor

(`bh_graph.gw250114`, Fig 47.) O4b PE samples are not yet on the public GWOSC
API (checked through GWTC-4.1, coverage ends Jan 2024), so: paper medians
($33.6/32.2\,M_\odot$) through Kerr $\eta_A$ give $0.3$–$0.4$ at $a_f \sim
0.7$ — showing the quoted range *requires* the Kerr correction
(Schwarzschild-only gives $\sim 0.45$) — with $E_{rad} \sim 5\%$, far from
any fission corner (ordinary GR merger in our reading). `check_o4b_public()`
pulls real PE samples the moment they land and re-runs Appendix W per-sample;
it reports "not yet public" today, never fake data. SYK-24 on Quantinuum H1
(Granet et al., arXiv:2507.07530, TETRIS, Loschmidt decay to $Jt \sim 1$)
added as 9th literature anchor: sparse random all:all scrambles on hardware.

![Fig 47](../figures/fig47_gw250114.png)

## Appendix AZ. Overtone tower from leaky cavities; tension no-go

(`bh_graph.overtones`, `bh_graph.tensionvol`, Fig 48.) Fitting a
Poschl-Teller barrier to the fundamental only ($b = 1/2\mathrm{Im}\,\omega_0$)
predicts the damping ladder $1$:$3$:$5$ vs GR's $1$:$3.08$:$5.38$ (Leaver) —
within $8\%$ with zero additional parameters: tower *structure* from
leaky-cavity physics, absolute scale from Appendix AG, exact numbers still
GR's (Regge-Wheeler potential needed for those). Tension-from-complexity was
attempted and honestly failed: bridge volume energy $E = \rho A d$ leaves
$\rho$ undetermined over $\sim 100$ orders (Planck vs Hawking density), with
Planck tension exceeding the hole's own mass (absurd) — so $\sigma$ stays a
bounded parameter (Appendix AX), and the missing microphysics is localized
to the bridge interior equation of state, not bluffed.

![Fig 48](../figures/fig48_overtones.png)

## Appendix BA. Big SYK to $N = 24$: flat $t^*$, MSS headroom holding

(`bh_graph.sparse24`, Fig 32 extended.) Stabilizer-tableau triplet builder
($N = 24$: 10626 terms, dim 4096, $\sim 4$ s build, verified against dense
ED) with thermal typicality OTOCs: infinite-$T$ $t^*$ flat at $1.28$–$1.30$
from $N = 8$ to $24$ while the chain climbs $1.8 \to 7.4$; thermal
$\lambda/2\pi T$ at $\beta = 1$ reads $0.68, 0.66, 0.86, 0.77$ at $N = 10, 16, 20, 24$ — below 1 throughout, trending upward within fit noise (unregularized thermal OTOC, 2 disorder samples).
Saturation approached, not claimed — finite-size fits at dim $\le 4096$.
![Fig 32](../figures/fig32_bigscaling.png)

## Appendix BB. Light bending passes, Mercury gaps (my bet lost)

(`bh_graph.lensing`, Fig 49.) Fermat paths in $n(r) = 1/c_{eff}$ with
$c_{eff} = 1 - R_s/r$ give $4M/b$ at first order — full GR, not half
(the factor-2 shortfall belongs to $v_{coord} = 1 - M/r$ models; ours was
calibrated to the full Schwarzschild coordinate speed, so the naive failure
I predicted does NOT occur — recorded as a lost bet). Second order differs
($c_1 = 3.36$ vs GR $1.94$), currently untestable. Mercury/orbits fail
cleanly: Appendix AS gives closed Newtonian ellipses ($0$ vs $43''$/cy) —
the missing piece is precisely the spatial/post-Newtonian sector ($g_{rr}$),
which no appendix currently derives. Light never needed it; orbits do.

Extension (`bh_graph.chroma`, Fig 55): Fermat uses *phase* velocity, so
lensing goes chromatic as $n(r,\omega) = n_{geom}(r)\,n_{disp}(\omega)$ with
$n_{disp} - 1 = (\omega/\omega_P)^2/24$ (phase $1/24$, not group $1/8$ —
conflating them would triple the effect). Since $n_{disp}$ is $r$-independent
it factors out of Born exactly: fractional chromaticity $= (x^2/24)/(1-x^2/24)$,
$\sim 10^{-56}$ optical to $\sim 10^{-32}$ at 10 TeV — achromaticity holds by
$\sim 50$ orders over multi-wavelength tests ($\sim 10^{-3}$). A null
prediction with an exact scaling law, not a signal.

Extension (`bh_graph.shapiro`, Fig 49, third panel): the same $c_{eff}$
gives Shapiro delay for free — $\Delta T = \int(1/c_{eff} - 1)\,dl$
reproduces GR's $R_s\ln(4r_1r_2/b^2)$ leading logarithm (tested to 5%),
so Cassini's $\gamma - 1 = (2.1 \pm 2.3)\times10^{-5}$ passes with our
$\gamma = 1$ exactly. Light-propagation tests now stand three-for-three
at first order (bending, Shapiro, achromaticity); orbits remain the open
sector.

**Update (BH):** the orbit sector is now closed — see Appendix BH. The
missing $g_{rr}$ is derived from leg tortuosity ($h = (1+x/2)^2$,
$\gamma = 1$), and Mercury integrates to 42.99"/cy. BB's "orbits fail
cleanly" stands as the recorded miss, corrected in-text per convention.

![Fig 55](../figures/fig55_chroma.png)

![Fig 49](../figures/fig49_lensing.png)

## Appendix BC. $b_{crit}$: isotropic reading dies at $8M$, tangential constrained

(`bh_graph.bcrit`, Fig 50.) Bouguer's invariant in the AT medium extended
isotropically on flat space: turning function $n(r)r = r^2/(r-R_s)$ minimized
at $r = 2R_s$ gives $b_{crit} = 8M$ — $54\%$ above GR's $3\sqrt{3}M$, excluded
by EHT's shadow ($\sim 15\%$ combined) at $\approx 3.6\sigma$ (not $5\sigma$ —
stated). This kills the *isotropic extension*, not the core: radial AT
calibration, weak-field results, and the $4M/b$ first-order bending all stand.
Constructive consequence: transverse propagation must differ from radial —
near-horizon tangential motion must be $\sim$unimpeded (fast), exactly as the
all:all interior independently demands (Sec 1). EHT's shadow thereby becomes
a quantitative target: any transverse completion (anisotropic effective
geometry or $g_{rr}$ spatial curvature) must land $b_{crit}$ in $[4.42, 5.98]M$.

![Fig 50](../figures/fig50_bcrit.png)

## Appendix BD. Lattice dispersion: quadratic by symmetry, Fermi-safe by 8 orders

(`bh_graph.dispersion`, Fig 51.) Hopping on discrete legs implies lattice
dispersion $\omega = 2J|\sin ka/2|$, $v_g = Ja\cos ka/2 \to 0$ at the
Brillouin edge. Since $v_g$ is even in $k$, there is NO linear term:
$\delta v/v = (ka)^2/8 + \cdots$ — the strong Fermi linear bounds
($E_{QG,1} > 9.3\times10^{19}$ GeV) are evaded by symmetry, not tuning.
Effective quadratic scale $\sqrt{8}\,E_P \approx 2.8\,E_{Planck}$ vs Fermi
quadratic $1.3\times10^{11}$ GeV: safe by $\sim 10^8$ (a 10 GeV GRB photon
over 3 Gpc delays $\sim 10^{-20}$ s). Caveats: regular-lattice result (no
$k$ exists in all:all regions); near-horizon running of effective spacing
open; scalar only, no birefringence prediction.

> **Vacuum Dispersion and Discrete Leg Symmetry.**
> The discrete leg network induces an effective chromatic dispersion on null
> trajectories. Owing to the inversion symmetry $k \leftrightarrow -k$ of the
> regular ambient lattice, the odd-power dispersion terms vanish identically
> ($E_{QG,1} = \infty$). The leading-order correction is purely quadratic in
> photon energy (group velocity, subluminal):
> $$v(E) = c\left(1 - \frac{E^2}{E_{QG,2}^2}\right), \quad \text{with } E_{QG,2} = \sqrt{8}\,E_{Planck} \approx 3.45 \times 10^{19}\,\text{GeV}$$
> This prediction establishes a sharp falsifiability criterion: detection of
> any linear-LIV signal (finite $E_{QG,1}$) falsifies the discrete-leg
> topology, whereas a measured sub-Planckian quadratic delay
> ($E_{QG,2} \sim \mathcal{O}(E_P)$) fixes the effective spatial leg spacing
> up to $O(1)$ lattice factors. Current astrophysical constraints (Fermi-LAT
> GRB limits $E_{QG,2} \gtrsim 10^{11}$ GeV) lie approximately eight orders
> of magnitude below this Planck-scale threshold, ensuring full compatibility
> with existing observational data.

![Fig 51](../figures/fig51_dispersion.png)

## Appendix BE. Footprint corrections to ringdown: comb, echoes, $\ell$-cutoff

(`bh_graph.qnmfoot`, Fig 52.) Three finite-$k$ effects: (1) mass ladder
$M_k = \sqrt{k/16\pi}$ makes QNMs a comb with fractional spacing $1/2k$
($\sim 10^{-77}$ astrophysically — derived, unobservable, stated), $\to$ GR
as $k \to \infty$; (2) echo trains $h = \sum R^n h_{RD}(t - n\Delta t)$
with our $\Delta t(M)$, reflectivity $R$ postulated (leg S-matrix open) —
LVK echo nulls bound $R$ in principle, a matched-filter search we don't run
(note: echoes vanish as $\omega \to 0$, not as $k \to \infty$); (3) angular
cutoff $\ell(\ell+1) \le k$ ($\to$ GR as $k \to \infty$): irrelevant at
$k \sim 10^{77}$ ($\ell_{max} \sim 10^{38}$) but sharp for micro-holes
($k \sim 100 \to \ell \le 9$) — the one footprint signature that bites
where $k$ is small.

![Fig 52](../figures/fig52_qnmfoot.png)

Extension (`bh_graph.qnmlegs`, Fig 53): leg quantization via the first law
gives transition lines $\omega_n = n/32\pi M$, a factor $\approx 37.6$ finer
than the QNM fundamental — $\sim 5$ Hz at $63\,M_\odot$ (below band; only
$\lesssim 10\,M_\odot$ holes peek above 10 Hz), with single-quantum energy
fraction $\sim 10^{-41}$ (incoherent fine structure, invisible next to
coherent ringing). Microstate broadening $\delta\tau/\tau \sim 1/\sqrt{k}
\sim 10^{-39}$; lattice reflectivity $R \sim (\omega/\omega_P)^2$ closes
item (2)'s open $R$: echo energy $\sim 10^{-160}$ at 100 Hz — discreteness
echoes unobservable, from this mechanism, by a quantified margin.

![Fig 53](../figures/fig53_qnmlegs.png)

## Appendix BF. Wave lab: dephasing on defective fabric, measured

(`bh_graph.foamgrid`, Fig 56.) FDTD scalar waves on a 2D grid with per-edge
speed defects ($c^2 = 1 + \varepsilon M$, pulsed Gaussian-beam source):
centroids stay unbiased (jitters, averages straight — tested); transmission
deficit grows $\propto \omega^2$ (16% $\to$ 4% $\to$ 0.2% across $\lambda =
8 \to 32$ cells at $\varepsilon = 0.25$) — faster phase rotation samples
defects harder, exactly the proposed mechanism. Calibrated extrapolation
($\delta\phi^2 = C(k\varepsilon a)^2 N_{edges}$) turns sharp-image data into
a fabric-cleanliness bound: per-Planck-edge fluctuations $\varepsilon
\lesssim 10^{-3}$ (optical/Gpc) and $\lesssim 10^{-14}$ (TeV/Gpc), assuming
independent edges (correlated patches of $\xi$ edges relax this by
$\sqrt{\xi}$ — stated). Static disorder only: no foam dynamics smuggled in;
quantized fluctuating wirings remain open (see discussion of item 2/3).

![Fig 56](../figures/fig56_foam.png)
## Appendix BG. Persistent walks: dilation derived, drift cubic, spin effaced

(`bh_graph.perwalk`, Fig 57.) Massive walkers split fixed-length hops between
translation and internal cycles: $v^2 + r_{clock}^2 = c^2$, so clocks tick at
$\sqrt{1-v^2}$ by counting (linear $1-v$ would be wrong — tested via 3-4-5
triangle). Degree-biased hopping on flux-conserved pileup $d \propto 1/r^2$
gives drift $\propto 1/r^3$, *not* Newton $1/r^2$ (measured slope $\approx
-3$): heterogeneity alone cannot source gravity, proving Appendix AS's
temperature factor load-bearing rather than decorative. Heading memory $\mu$
tunes trajectories diffusive ($\alpha \approx 1$) to ballistic ($\alpha
\approx 2) without closing orbits — momentum memory is demonstrated, true
inertial trajectories still need calibration ($\tau_p$ open). Spin as
internal circulation leaves mean drift unchanged to first order (effacement
toy), and Mathisson-Papapetrou for Mercury is $\sim 4\times10^{-14}$ of
Newtonian — the spin question answered: negligible, quantified.

![Fig 57](../figures/fig57_perwalk.png)

## Appendix BH. Strain corrected: tortuosity gives $\gamma = 1$, Mercury 42.99"

(`bh_graph.strain`, Fig 58.) The proposed $dl = dr/(1-\sqrt{\chi})$ is
excluded: it gives $h = 1/(1-x)^2$, $\gamma = 2$, missing Cassini by
$\sim 50{,}000\sigma$ (locked as `test_gamma_corrected_vs_naive`), and
its $c_{eff}$ contradicts Appendix AT. The consistent tortuosity form
$dl = (1+\sqrt{\chi}/2)\,dr$ gives $h = (1+x/2)^2 \approx 1+x$ via
$\sqrt{\chi} = R_s/r$ (Appendix AW), hence $\gamma = 1$ exactly,
$c_{eff} = \sqrt{f/h} = 1-x$ matching AT to first order, and $b_{crit}$
back to $3\sqrt{3}M$ (BC target — $f$ alone fixes the photon sphere).
Mercury precession measured by direct geodesic integration
($\phi$-domain orbit equation, complex-step derivatives, refined
perihelion tracking): GR Schwarzschild 42.99"/cy (validates the
integrator), model 42.99"/cy (identical — differences are $O(x^2)$),
flat-$h$ hybrid 28.7" (PPN $2/3$ factor reproduced). The BB Mercury gap
is closed: the missing $g_{rr}$ sector is now derived, not calibrated.

**Logical status (Route A).** The tortuosity picture above is illustrative,
not load-bearing: $h$ is already fixed by consistency — AS's potential plus
BB's $4M/b$ bending force $\gamma = 1$ in any metric reading, hence $h
\approx 1+x$, and $c_{eff} = \sqrt{f/h} = 1-x$ matches AT to first order
(locked as `test_consistency_chain_ceff`). The live assumptions are the
metric framework itself (angular $r^2 d\Omega^2$ included) and the inherited
AT $\alpha = 1$ calibration. Appendix BI attempts the genuine
from-micro derivation via Ollivier-Ricci.

**Fitted-parameter audit.** The $1/2$ in $h = (1+x/2)^2$ is **fitted**,
not derived: it is the unique coefficient giving $\gamma = 1$ and hence
Mercury. It is recorded here as a fit so no reader mistakes the tortuosity
picture for a derivation of the coefficient. Full parameter status:

| parameter | value | status |
|---|---|---|
| tortuosity $1/2$ | $0.5$ | fitted to $\gamma = 1$ (this appendix) |
| AT $\alpha$ | $1$ | calibrated to Schwarzschild $c_{eff}$ (BB) |
| $k(M) = (4\pi/\ln 2)M^2$ | — | GR-consistency input (Sec 2; see audit below) |
| $s_{leg} = \ln 2$ | $0.69$ | **measured saturation** (BN; B retired by BS flip) |
| $k_{crit}$ | embedding | heuristic $\to$ formalized in BK |

**Circularity audit for $k(M)$.** The circle is real and is not hidden:
$k(M)$ enters through GR consistency, and the gravity derivations (BB, BH,
BI) spend it to convert leg counts into $R_s/r$. Given $k(M)$, what is
genuinely derived: the $1/r$ dependence, $\gamma = 1$, Mercury's $43''$,
$b_{crit} = 3\sqrt{3}M$. What is not: any mass scaling — the theory does
not predict how $k$ grows with $M$ from microphysics (Appendix B derives
$k(N)$, not $k(M)$). A referee aiming here aims at the admitted joint.

![Fig 58](../figures/fig58_strain.png)

## Appendix BI. Weak-field Ollivier-Ricci: sign derived, scaling suggestive

(`bh_graph.weakfield`, Fig 59.) Ambient $L^3$ grid plus hub, stubs attached
by pure flux ($P \propto 1/r^2$ — geometric input, nothing tuned), two
attachment modes. Measured radial OR curvature is **negative in every
configuration** (both modes, all seeds, all stub counts): mass stretches
radial rulers, the correct sign for $h > 1$, against the naive
hub-shortcut intuition (which predicted positive). Scaling is suggestive
but unresolved: direct mode gives exponent $p = 0.92 \pm 0.48$ ($L = 9$,
6 seeds) and the $1/r$ collapse beats $1/r^2$ (CV $0.47$ vs $0.60$),
while chains sit at $p = 1.30 \pm 0.31$ with tied CVs. The pre-registered
bar (direct $p \in [0.7, 1.3]$) is met by the mean but not cleanly —
recorded as a **partial** micro-derivation: sign from micro, scaling and
coefficient still open, awaiting bigger lattices.

![Fig 59](../figures/fig59_weakfield.png)

## Appendix BJ. PPN status table + second-order peel-off law

(`bh_graph.strain`, Fig 60.) The post-Newtonian ledger, all entries:

| quantity | GR | model | status |
|---|---|---|---|
| $\gamma$ | 1 | 1 exactly | derived (BH tortuosity) |
| light bending | $4M/b$ | $4M/b$ | derived (BB) |
| Shapiro $\gamma$ | 1 | 1 | derived (BB/Shapiro) |
| Mercury | $43''$/cy | 42.99" | measured by integration (BH) |
| $\beta$ | 1 | — | **unresolved** (coordinate-confused; not quoted) |
| $\alpha_{1,2}, \xi$, Nordtvedt | 0 | — | untouched |
| 2nd-order bending $c_1$ | 1.94 | 3.36 | pre-registered wire (AN/6) |
| 2nd-order peel-off | 0 | $-0.75\,M/a$ | **measured here** |

The last row is new: ours-vs-GR perihelion difference follows
$(ours - GR)/GR = -0.75\,M/a$ ($4.1\%$ at $a = 20M$ down to $2\times10^{-8}$
at Mercury — second-order structure confirmed numerically, unobservable in
the solar system). The model is GR to first PN order with a quantified,
falsifiable-in-principle second-order departure.

![Fig 60](../figures/fig60_divergence.png)

## Appendix BK. Formal $k_{crit}$ + $s_{leg}$ delimitation (no figure — formal)

(`bh_graph.micro`: `packing_kmax`, `footprint_deficit`, `pop_forced`.)
**Theorem-in-toy (pop forced).** Given the patch postulate (each exterior
leg occupies $\ge l_p^2$ of footprint), no embedding of $k$ legs exists
through $r_{foot}$ for $k > \lfloor 4\pi r_{foot}^2/l_p^2 \rfloor$ — the
horizon pop is then a packing necessity, not a dynamical postulate. The
code locks the boundary: `packing_kmax(R_POINT,1) = 12`, pop unforced at 12,
forced at 13, consistent with the Sec 3 heuristic. What remains
postulated is exactly one thing: the patch size $4\ln 2\,l_p^2$ per leg (BS: derived
from measured $\eta_{vN}$, not assumed — see BS).

**Postulate box ($s_{leg} > \ln 2/2$; saturation $s_{leg} = \ln 2$).** Appendix C
needs $s_{leg} > \ln 2/2 \approx 0.347$ for the QES crossing (BS flip). Domain:
random tensor networks and area-law ground states (measured $0.69$ random,
$0.55$ critical Ising — AN wire 4, clearance $1.6\times$). Separately, vacuum
legs saturate at $s_{leg} = \ln 2$ (BN-measured), which via patch $= 4\ln 2$
gives $\eta = 1/4$ exactly (BS). Crossing bound vs saturation value are
different quantities — conflating them caused the BN false alarm.

## Appendix BL. Hamiltonian sketch + small-$N$ leg check (labeled sketch)

(`bh_graph.legham`, Fig 61.) The sketch: $H = H_{SYK}(interior) +
H_{legs} + H_{ambient}$, with $H_{legs} = \lambda\sum_{i<j \in legs}
ig_{ij}\chi_i\chi_j$ a weak quadratic Majorana field on the legged subset
(Hermitian bilinear — the bare $\chi_i\chi_j$ is anti-Hermitian and
vanishes under symmetrization, a bug caught by the suite). Small-$N$ ED
($N = 8$): $t^*$ unmoved at $\lambda = 0.1$, barely shifted at $1.0$,
$\sim 2\times$ slower at $3.0$ — weak legs preserve the fast scrambler,
strong legs break it. This is a consistency check on a sketch, not a
dynamics: unitarity of leg surgery, backreaction of $k$-change on the
spectrum, and the ambient coupling are named known-unknowns, unsolved.

![Fig 61](../figures/fig61_legham.png)

## Appendix BM. Reduction theorem: $k(M) \iff R_s(M)$ (no figure — formal)

(`bh_graph.horizon`: `k_from_mass_via_rs`, `schwarzschild_rs`, `k_from_rs`.)
**Theorem.** Given the patch postulate ($k = A/4\ln 2\,l_p^2$, BS) and sphere geometry
($A = 4\pi R^2$), the mass map $M \mapsto k$ factors entirely through the
radius map $M \mapsto R_s$: $k(M) = 4\pi R_s(M)^2/4\ln 2\,l_p^2$. The code takes
$R_s(M)$ as an explicit function argument — pass $2M$, get $(4\pi/\ln 2)M^2$;
pass $3M$, get $9$ times that (locked as `test_reduction_theorem`). The
admitted circle of BH's audit is thereby shrunk to exactly one statement:
$R_s = 2M$, the vacuum Schwarzschild relation. Deriving $k(M)$ from
microphysics is equivalent to deriving vacuum GR; there is one target,
not a web. (Scaling remark: $R_s \propto M$ alone follows from dimensional
analysis + scale invariance — the unfactorable residue is the pure number
$2$.)

**Anchor note.** Until derived, $R_s = 2M$ is taken as a *measured input*
(light deflection, Shapiro, EHT shadows, Sgr A* orbits confirm it
independently of this model) — the theory's $G$, not a vicious circle
(Verlinde takes $G$ the same way): vicious would be claiming to derive it
while assuming it, which the audit above preempts. Two GR-free derivation routes are queued: statistical
mechanics (spectral $T(k)$ + equipartition + legs-as-bits, blocked on a
Hamiltonian) and Jacobson completion (blocked on Raychaudhuri + BO
mechanism).

## Appendix BN. Jacobson bridge 2: constancy passes, $\eta$ exposes $\ln 2$

(`bh_graph.jacobson`, Fig 62.) The cheapest Jacobson falsifier, run first:
$S_{ent}/k$ across random star-TN cuts ($N = 8$ bulk, $k = 1$–$4$, 12
seeds each). **Constancy passes:** drift $< 0.8\%$ — the area law with
universal coefficient holds in the $k$-limited regime (local Rindler cuts
always are). **Coefficient exposes:** $\eta = 0.69 = \ln 2$ (qubit legs),
not the $1/4$ the AU chain assumes — face-value $G = 1/4\eta = 0.36 \ne 1$.
Two resolutions, no bluffing: **(A)** the leg patch is $4\ln 2 \approx
2.77$ Planck areas (recalibrates $A = k\,l_p^2$, $k(M)$, $k_{crit}$ — major
surgery, all coherent); **(B)** physical legs carry $1/4$ nat sub-maximally
(keeps patch $= 1$, needs a dynamical reason — new open assumption).
Bridges 3 (scaling) and 1 (modular Hamiltonian) are gated on resolving
this; running them first would build on a $2.77\times$ crack.

**Update (BO):** resolution **B adopted** — then **reversed by BS** (see below):
the vN/thermo audit showed A dissolves two debts (BN mismatch + B mechanism)
while B keeps both. **A adopted:** patch $= 4\ln 2$, legs saturate, $\eta =
\ln 2/4\ln 2 = 1/4$ exact, $G = 1$ — measured, no postulate. Bridges 3/1
proceed on measured $\eta$.

![Fig 62](../figures/fig62_eta.png)

## Appendix BO. Postulate B adopted, then retired by BS (history preserved)

(`bh_graph.jacobson`: `postulate_B_closure`, since removed.) **Postulate B
(retired).** Physical leg states were taken to carry exactly $1/4$ nat
each; the random-tensor $\ln 2$ was read as a kinematic maximum above the
physical value. Consequences (then locked): $\eta = 1/4$, $G = 1$, $S = k/4$,
Clausius $\varepsilon = \kappa/8\pi$ — the AU chain closed with patch $= 1$
Planck area intact. **Why B was chosen:** it preserved Sec 2's $A = k\,l_p^2$
exactly and localized the new assumption to one number. **Why reversed (BS):**
the vN/thermo audit showed the mismatch was a category error — BN measured
vN capacity ($\ln 2$) while B assigned thermo value ($1/4$) — and option A
(measured $\eta_{vN}$ + patch $4\ln 2$) dissolves both the mismatch and B's
mechanism debt with zero new assumptions. B's ledger entry is kept here so
the reversal is on the record; the live theory is A (BS).

## Appendix BP. Walk no-go + fluctuation escape: BG solved modulo one assumption

(`bh_graph.perwalk`, Fig 63.) **No-go theorem-in-toy.** Any walk with hop
weights a smooth function of local degree drifts $\propto (w'/w)\,d'(r)$;
with ambient background $d \to d_0$, the exponent is $-3$ for *every*
smooth $w$ — locked for linear, sqrt, saturated, and even tuned-exp-root
(all $-2.99$). The only weight escape is the background-subtracted
$e^{2\sqrt{d-d_0}}$ monstrosity (exactly $-2.0$), documenting that
weight-rules cannot honestly reach Newton. Constant persistence cannot
either: $v = b/(1-\mu)$ inherits $b$'s $-3$ exactly (the $d_f = 1$
trajectory-dimension proposal dies here — persistence rescales
coefficients, never exponents). **Escape.** Persistence from local
fluctuations, $1 - \mu = c\sqrt{\chi}$ (walker sees leg density, never
$r$): $v(r) = b(r)/(1-\mu(r))$ has exact slope $-1.95 \approx -2$, and the
amplification law $v = b/(1-\mu)$ is validated by simulation to a few
percent. BG is solved modulo the labeled $\sqrt{\chi}$ assumption
(fluctuation story, not derived) — parallel to BH's fitted $1/2$, queued
for the same micro-derivation campaign.

![Fig 63](../figures/fig63_muchi.png)

## Appendix BQ. External review kills + Green-function walk fails by shorting

(`bh_graph.weakfield`, Fig 64.) An external model review (Gemini) killed
two programs, both verified independently here. **S-wave superposition:**
$\mathbb{E}[|S|] = \frac{\sqrt{\pi}}{2}\sqrt{k}$, not $\sqrt{k}$ (11.4%
shortfall — RMS/expectation conflation, confirmed numerically), 52%
metric speckle (measured 0.522, excluded by Cassini at $10^{10}$), plus
multi-body interference and cherry-picked $1/\sqrt{4\pi}$ — cut, all five
holes fatal. **Dephasing exponent $-1/4$:** dilute scattering gives
$l_\phi \propto n_d^{-1}$ universally, and disorder area $\sim \chi^{-1/2}$
demands infinite influence at large $r$ — cut. The review's best proposal
(Green's-function drift) was tested on the actual topology and **fails by
shorting**: hitting probability $h(2)/h(6)$ drops $9.2 \to 4.1$ from 0 to
60 stubs — more legs flatten harmonic gradients (anti-gravity scaling),
the Sec-1 small-world mechanism striking again. Poisson far-field stays
$\sim A/r + B$ but legs only degrade the fit ($3\% \to 17\%$ residual;
mass $=$ input charge). Temperature (AS) remains load-bearing — BG's
lesson confirmed from a third direction.

![Fig 64](../figures/fig64_green.png)

## Appendix BR. Entropy-capacity tension: resolved by BS (history preserved)

(`bh_graph.tn`: `interior_capacity`, `required_entropy`, `max_consistent_n`,
`capacity_violated`.) **Theorem-in-toy.** Given (i) $E = \varepsilon N$
with fixed $\varepsilon$ (B/M), (ii) $S_{ext} = k\ln 2$ (BS: saturated legs),
(iii) an $N$-qubit interior, (iv) pure total state: $k\ln 2 = S_{ext} =
S_{int} \le N\ln 2$ forces $k \le N$, but fixed-$\varepsilon$ $k/N$ grows
unboundedly — violated past $N_{max}$ ($= N_{match} = 25$ at repo $\varepsilon$,
identically; a finite $N_{max}$ exists for *any* constant $\varepsilon$).
**Resolved by BS:** $\varepsilon$ runs as $c/\sqrt{N}$ (temperature-like),
$N$ goes holographic ($N \propto M^2$), $k = N$ exactly, margin $= 4\ln 2$.
The vN/thermo audit (Page/QES/Clausius all formula-level thermodynamic; BN's
SVD the only genuine vN entropy) confirmed the tension was about microstate
housing, settled by running $\varepsilon$ + saturated legs. (c) partially
true throughout (no interior factor ever constructed); (a) subsumed (wirings
counted, no fractional states — $e^{k\ln 2} = 2^k$ integer).

## Appendix BS. The flip to A+(b*): legs saturate, $\varepsilon$ runs (Fig 65)

(`bh_graph.horizon` `PATCH_AREA`, `bh_graph.tn` running-$\varepsilon`,
`bh_graph.jacobson` `measured_eta_closure`.) The vN/thermo audit (Page,
QES, Clausius all formula-level thermodynamic; BN's SVD the only genuine
vN entropy) showed BN's $\eta_{vN} = \ln 2$ vs $1/4$ "mismatch" was a
category error — capacity vs assignment — and option A dissolves it plus
Postulate B's mechanism debt with zero new assumptions. **Adopted:**
patch $= 4\ln 2$ Planck areas per leg (from measured $\eta_{vN}$ + $G = 1$
units), legs saturate ($s_{leg} = \ln 2$), $\eta = \ln 2/4\ln 2 = 1/4$
exact, $G = 1$, $k(M) = (4\pi/\ln 2)M^2$. **Adopted (b*):** $\varepsilon$
runs as $c/\sqrt{N}$ (temperature-like, $c = \sqrt{4\ln 2/16\pi}$ from the
crossover identity), $N$ goes holographic ($N \propto M^2$), $k = N$
exactly, $\alpha = 1$ (the growing-$\alpha$ corollary revised — it holds
only for the fixed-$\varepsilon$ matching form), capacity margin $= 4\ln 2$.
Entropic Newton preserved exactly (equipartition over Planck bits
$N = k\cdot 4\ln 2$, $G = 1$ locked by the chain test). QES transition
bound moves to $\ln 2/2$ (AN wire 4 margin $2.2\times \to 1.6\times$, no
trip). **Ledger: 6 assumptions $\to$ 4** (measured $R_s$, fitted $1/2$,
calibrated $\alpha$, assumed $\mu(\chi)$), **zero mechanism debts** — every
survivor is an input, fit, calibration, or labeled assumption, no
unexplained numbers.

![Fig 65](../figures/fig65_flip.png)

## Appendix BV. UV tortuosity-as-scattering: $c$, $p$, $\gamma$ from $\ln 2$ (Figs 70–72)

(`bh_graph.uvscatter`.) Lettering note: BT–BU live on main (2PN IR battery +
leg-shedding kilonovae); this branch continues at BV for merge compatibility,
and quotes main's BU numbers ($p = 0.913 \pm 0.049$, $\beta(N)$, $c_1 = 3.36$,
$w = 1.953$) as comparison targets only — nothing below takes them as input.

**Motivation.** BH fitted the tortuosity factor $1/2$ to $\gamma = 1$ and BU
(main) fitted the radial exponent $p$ and bridge law $\beta(N)$ to the J0737
2PN cancellation. Three open entries, one mechanism: exterior legs are radial
line defects of cross-section $\sigma = 4\ln 2\,l_p^2$ (BS patch postulate),
and graph walks scatter off them with entanglement cost $s_{leg} = \ln 2$ per
encounter (BN-measured saturation). The dilute-line tortuosity of this porous
medium derives $c$, hence $p = 2c$, $\gamma = 2c$, and the pop at $\chi = 1$.

**Micro identities (zero new assumptions).** $k$ legs piercing a sphere of
radius $r$ give 2D density $\rho_{2D} = k/4\pi r^2$ and occupied area fraction
$\chi(r) = \rho_{2D}\sigma = k\sigma/4\pi r^2$. With $R_s = \sqrt{k\sigma/4\pi}$
(the radius where $\chi = 1$) and $x = R_s/r$: $\chi = x^2$ exactly. The pop
$k_{crit} = 4\pi r^2/\sigma$ is the BK packing theorem restated ($r = 1.6\,l_p
\to k_{crit} = 11.6$, matching `packing_kmax` exactly). Mean transverse spacing
$d = r\sqrt{4\pi/k}$ and exclusion radius $r_e = \sqrt{\sigma/\pi}$ give the
detour fraction $r_e/d = \sqrt{\chi/\pi}$ (identity), so $dl/dr = 1 + x/\sqrt\pi$
for unit detour efficiency: $c_{geom} = 1/\sqrt\pi = 0.564$ with $f = 1$.
Comparing $h = (1+cx)^2 \approx 1 + 2cx$ with $g_{rr} = (1+U)^{2p} \approx 1+px$
($U = x/2$) gives $p = 2c$; with $f = 1-x$, $\gamma = (h-1)/(f^{-1}-1) = 2c$.
One packing number predicts the radial exponent, the PPN parameter, and via
$c_2(p) = p(2p-1)$, $c_{tot} = 3.36 + 1.953\,c_2$ the 2PN cancellation.

**Simulation design.** $L^3$ cubic lattice (ambient graph, mean degree ~6),
core = nodes within $1\,l.u.$ of center (the all:all interior, never blocked),
$k$ radial rays in Fibonacci directions (the exterior legs). Three modes:
**hard** (BFS avoiding cylinders $d < 0.9\,l.u.$), **soft** (Dijkstra with
Gaussian edge cost $w = 1 + \alpha e^{-d^2/2r_e^2}$, $\alpha = \ln 2$,
$r_e = 0.60\,l.u.$ from $\sigma = 1.139\,l.u.^2$ at $a = 1.56\,l_p$), **mixed**
(hard core $d < 0.75\,r_e$ + soft Gaussian outside). Observable per radial
shell: $tort = d_{graph}/r$, $tort_{clean}$ on the undefected lattice
(Manhattan baseline $\sim 1.35$), excess $= tort/tort_{clean} - 1$ (the ratio
cancels the lattice baseline and core-source convention), $c = excess/x$.
Dilute fit over $\chi < 0.2$ shells inside the inscribed sphere (box corners
excluded). Estimators (median/mean/regression) agree within $0.15$.

**Results (Fig 70).** Soft $\alpha = \ln 2$, L=32: $c = 0.437$ ($k = 20$),
$0.636$ ($k = 80$), $0.681$ ($k = 160$); L=64, $k = 160$: $0.603$. The $k = 20$
point lands $0.2\sigma$ from the BU-implied $0.456$ with zero tuning; the
high-$k$ asymptote $\approx 0.60$ matches $c_{geom} = 0.564$. Orientation ensemble
(6 random leg-pattern rotations): std $0.011$ — $c$ is not a lattice-alignment
artifact; shell scatter ($\sim 0.10$) dominates the quoted band. The $c(k)$ rise
is void closure: sparse legs leave void channels walks slip through ($f < 1$);
dense legs are unavoidable ($f \to 1$) — the same disorder that pulls $0.5$ to
$0.456$. Hard walls give $c = 0.66$ at $k = 10$ (2× soft, overshooting toward
the naive $1.1$–$1.6$) and pop already at $k = 20$ (reachable $0.2\%$): too
strong and brittle, as expected for infinite barriers vs $\ln 2$ soft cost.
Mixed ($0.75\,r_e$ core): $0.451$ ($k = 20$), $0.827$ ($k = 40$), disconnected
at $k = 80$ — dilute value, pre-pop rise, then horizon. Predicted
$p = 2c = 0.87$ ($k = 20$) sits $0.2\sigma$ from BU's measured $0.913 \pm
0.049$; $c_{tot}(0.87) = 4.79$ vs GR $4.8695$ ($\Delta = -0.08$, sub-$\sigma$
for J0737). The flat case $c = 0.25 \to p = 0.5 \to c_{tot} = 3.36$ stays dead
at $\Delta = -1.51$.

**Boltzmann layer (Fig 72).** Mean free path $\lambda_{mfp} = d = r\sqrt{4\pi/k}$;
optical depth $\tau = cx$ (extra path per unit path). Transport ladder at
L=12, $k = 10$: Dijkstra $0.33 \approx$ drifted finite-$T$ walks $0.37$–$0.76$
$<$ straight through-core rays $1.15$ — optimal routing is worth 3×, and
Boltzmann sampling agrees with Dijkstra within 2× at all $T$ (dilute detours
are perturbative). Bridge-exponent ladder for the BU $\beta(N)$ comparison:
$n(r) \sim r^2/F$ gives $\beta = 0, 1, 2$ for point/line/area footprints
$F = \lambda^2, \lambda a, a^2$; BU's fitted $1.24$ sits between line-like and
area-like — legs couple as lines with partial transverse resolution, and the
$1.5 \to 1.24$ drift is motion toward line-like as shells resolve. This
constrains $\beta$; it does not yet derive $1.24$ (queued: OR-gradient port).

**Pop without a metric (Fig 71).** Mixed L=32: reachable $0.99 \to 0.0002$
between $k = 40$ and $80$; theory $k_{crit}(r=2) = 44.1$ splits them, and
$\chi_{inner}$ crosses $1$ across the same step. The BK pop is graph
disconnection, no $g_{rr}$ written. UV running $p(\chi) = 2c(\chi)$: mixed
$k = 40$ rises $1.5 \to 2.8$ from $\chi = 0.03$ to $0.58$ (turnover at
$\chi = 0.06$), the emergent version of BU's fitted $p_{adj}(s)$ slope —
then paths vanish (turnover to pop, not flattening). Soft mode stays flat
($1.0$–$1.5$): Gaussian cost saturates at $1+\alpha$ instead of diverging.

**No-$r$ analysis (Fig 72).** Recomputing $\chi = k\sigma/4\pi r_{phys}^2$
with operational radius $r_{phys} = d_{clean}/T_0$ ($T_0 \approx 1.35$ the
once-measured clean-lattice ruler factor; $d_{clean}$ = Dijkstra distance
from the core) reproduces $c$ within $0.03$–$0.10$ across $L$, $k$. The
$\chi \to h \to p, \gamma$ chain never uses a background coordinate; $M \equiv
k$, $R_s$ is defined by $\chi = 1$. Full coordinate-freedom (random geometric
graph + OR-ball binning instead of a cubic lattice) is queued — the embedding
still uses coordinates; the analysis no longer does.

**UV sign check.** Radial Ollivier–Ricci on a defect-pierced weak-field graph
(L=7, $k = 4$ hard lines + flux stubs, exact LP): $\kappa = -0.148, -0.057,
-0.012$ per shell — negative everywhere. Attraction survives at $\chi \sim 1$;
a sign flip would have killed the model.

**Ledger: 4 assumptions $\to$ 3.** Tortuosity $1/2$ (fitted) $\to$ derived from
$s_{leg} = \ln 2$ + sphere packing ($c = 0.44$–$0.60$); $p$ (BU-fitted on main)
$\to$ predicted $0.87$–$1.2$; $k_{crit}$ heuristic $\to$ packing theorem
confirmed by disconnection. Remaining: $R_s(M)$ input, AT $\alpha$
calibration, $\mu(\chi)$ assumption. Honestly calibrated (not derived):
mixed-core fraction $0.75$ (0.5 blocks nothing, 1.5 pops at $k = 20$),
dilute cut $\chi < 0.2$, $T_0$ per $L$. Falsifiers armed: soft $c$ outside
$[0.3, 0.8]$ at any $k \ge 20$ kills the $\ln 2$ cost model; $\kappa \ge 0$ in
any UV shell kills attraction; pop location off $k_{crit}$ by $> 2\times$ kills
the packing pop.

**Scaling prototype for the N=4096 GPU run (`bh_graph.sinkor`).** Exact
N=1020 cost O(N³) Floyd $1.06\times10^9$ ops/graph; N=4096 exact would be
$64\times$ ($68.7\times10^9$/graph, $5.5\times10^{12}$ over 80 graphs) plus
12k Wasserstein LPs — a RunPod GPU job tracked as a GitHub issue, not a CPU
job. The CPU reference it ports is tested here: sparse Johnson matches Floyd
exactly (N=4096 in 1.7 s, 134 MB) and log-domain annealed Sinkhorn
($\epsilon = 0.01$) matches the exact LP to 4 decimals, reproducing the
weak-field radial slope $p = 0.940$ shell-by-shell — the exponent physics
survives the approximation. (Naive Sinkhorn stalls harmonically on OR cost
matrices because $C/\epsilon$ spans $10^{17}$; $\epsilon$-annealing
$1.0 \to 0.01$ with warm starts is load-bearing — the GPU port must keep
it.) The $\beta(4096)$ starting guess is $1.140$, band $[1.095, 1.185]$ from
the $1/N$ fit over BU points, GPU guess $1.18$ at the top (to be measured,
not fitted): one exact N=4096 graph at $\beta = 1.18$ with Sinkhorn OR tests
whether $p$ flattens/drops at $s < 5$ where $\chi \sim 0.2$–$0.5$.
