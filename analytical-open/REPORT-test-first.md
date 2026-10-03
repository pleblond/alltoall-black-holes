# What to test first

Validated against the frozen definitions in `src/bh_graph/backreaction.py`,
`src/bh_graph/accounting.py`, `src/bh_graph/split0.py`, and the I1 matching
in `docs/model.md`. No new ensemble was sampled. Every identity below is an
algebraic consequence of those definitions, or a Haar-average that is exact
for every finite \(N\ge 2\).

The result that changes the queue is the boundary information of one stored
pair. Several campaigns that look like the next step measure a different
object.

---

## Test 1 — histogram of \(B/q\) on a declared edge set

For an edge with endpoints \(i,j\), the repository defines

\[
B_{ij}=\Re(\psi_i^*\psi_j),\qquad
q_{ij}=|\psi_i|^2+|\psi_j|^2.
\]

With \(s=\psi_i+\psi_j\) and \(d=\psi_i-\psi_j\),

\[
|s|^2-|d|^2=4B_{ij},\qquad
|s|^2+|d|^2=2q_{ij},
\]

and the antisymmetric weight is exactly

\[
P_-=\frac{|d|^2}{|s|^2+|d|^2}
=\frac12-\frac{B_{ij}}{q_{ij}}
\qquad(q_{ij}>0).
\]

The isolated-channel information proposed for that weight is the binary entropy

\[
s_e=h_2(P_-)=h_2\Big(\frac12-\frac{B_{ij}}{q_{ij}}\Big),
\qquad
0\le s_e\le 1,
\]

with equality to \(1\) if and only if \(B_{ij}=0\), and equality to \(0\) at
the Cauchy–Schwarz ends \(B_{ij}=\pm q_{ij}/2\).

\(h_2\) is **not** an earned ledger entry. INFO-0 recorded counts with binary
logarithms and explicitly did not introduce \(-\sum p\log p\). The algebra
that converts \(B/q\) into \(P_-\) does not need that identification. The
numerical value of \(s_e\) does. Keep those two layers separate when a plot
is labeled.

### Three ensembles, three exact means

Summing \(s_e\) is meaningless until the edge set and the ensemble are fixed.
These three are theorems.

| Ensemble | Law of \(P_-\) | \(\langle h_2\rangle\) |
|---|---|---|
| Haar-random pure state, any \(N\ge 2\), any fixed pair | Uniform on \([0,1]\) | \(1/(2\ln 2)\approx 0.7213475\) bit |
| Equal moduli, uniform relative phase, **or** a real Gaussian pair | Arcsine (Beta \(\tfrac12,\tfrac12\)) | \(2-1/\ln 2\approx 0.557305\) bit |
| Real constant ground state of \(K_N\) (all-ones) | \(P_-=0\) on every edge | \(0\) |

The Haar row is exact at finite \(N\), not a large-\(N\) limit. Proof is in
`hidden-store-entropy/note.md`. A phase-randomized flat-magnitude vector is
not Haar and must not be used as the scrambled control. It sits on the
second row.

### Amplitude mismatch already forces the bit

Let one endpoint be a fixed real amplitude \(v>0\) and the other
\(\sigma g\) with \(g\) a standard complex normal (\(E|g|^2=1\)). Set
\(\lambda=\sigma/v\). Then

\[
x=\frac{B}{q}
=\frac{\lambda\,\Re g}{1+\lambda^2|g|^2}.
\]

Both \(\lambda\to 0\) and \(\lambda\to\infty\) send \(x\to 0\) in
probability, so \(h_2\to 1\) in probability. A cut leg whose two ends do
**not** carry comparable amplitude is already a one-bit channel, with no
dynamical selection of quadrature.

For small \(\lambda\),

\[
\langle x^2\rangle=\frac{\lambda^2}{2}+O(\lambda^4),
\qquad
1-\langle h_2\rangle
=\frac{\lambda^2}{\ln 2}+O(\lambda^4).
\]

### What to record on the first run

On one almost-all-to-all state, on three edge sets reported separately:

1. interior edges of \(K_N\);
2. the \(k\) cut legs only;
3. interior edges incident to a leg-bearing node (this set is a trap: its
   cardinality is \(\sim kN\), not \(k\)).

For each set report \(N_e\), the histogram of \(x=B/q\), the amplitude
ratio of the two ends, and \(\bar h=N_e^{-1}\sum h_2\). Do not fit
\(\bar h\). The three rows of the table are the controls.

Interpretation, before any dynamics:

- Interior Haar control must land on \(1/(2\ln 2)\). Any other mean means
  the ensemble or the estimator is wrong. Stop there.
- Cut legs with \(\lambda\ll 1\) or \(\lambda\gg 1\) must land near \(1\),
  with deficit \(\approx\lambda^2/\ln 2\). That would already saturate the
  I1 count of one bit per leg.
- A mean near \(0\) is the ground-state row. It does not test the scrambled
  horizon.
- A mean near \(0.557\) means the draw was real-Gaussian or
  equal-magnitude random-phase, not Haar.

Only a cut-leg histogram that matches none of these three is evidence that
a dynamical selection of \(B\) is doing something. That is the gate for a
later dynamics run, not the opening measurement.

### Coefficient, if the cut really is one channel per leg

I1a plus the matching theorem already say \(S=k\ln 2\) nats, hence \(k\)
bits, and \(A=4\ln 2\cdot k\,\ell_P^2\). Therefore

\[
\frac{S_{\mathrm{bits}}}{A}=\frac{1}{4\ell_P^2\ln 2}
\]

is the earned normalization, not a target to fit. Under the isolated-channel
sum \(S_Q=\sum_{e\in\mathrm{cut}} h_2(P_{-,e})\),

\[
\frac{S_Q}{k}=\bar h.
\]

- \(\bar h=1\) reproduces I1 with no free area per channel.
- Haar on the cut would give \(S_Q=k/(2\ln 2)\) bits, short of I1 by exactly
  \(2\ln 2\).
- Fitting a microscopic area \(a_\partial\) to force the match absorbs the
  discrepancy into geometry and hides which row of the table was measured.

\(B_{ij}=0\) is norm-neutral, \(\Delta\|\psi\|^2=2B_{ij}=0\). On \(K_N\)
every other node is a common neighbor, the cross sum in
\(\Delta E_\psi=2B-2\Sigma_{\mathrm{cross}}\) vanishes, and \(B=0\) is also
energy-neutral. On a cut leg the exclusive-neighbor sum survives, so
\(B=0\) does **not** imply \(\Delta E_\psi=0\). Energy-neutrality is the
wrong proxy on the horizon; \(B\) itself is the observable.

---

## Do not open with these

**Interior continuous dimension (BH-Q-ENT-0 style).**
For a region collapsed by \(n-1\) sum-maps, a boundary readout of rank at
most the boundary size \(b\) leaves

\[
D_Q\ge 2(n-1-b)
\]

blind real dimensions whenever the bulk relative modes are independent.
That is volume-leading. An area law for \(\dim Q\) is the wrong pass/fail
for the entropy above, which is at most one bit per **cut** channel and
does not grow with interior merges. Detail:
`bhq-boundary-scaling/note.md`.

**A campaign whose success condition is \(B_e=0\) from dynamics.**
Scale separation of the two endpoints already forces that limit. Measure
\(\lambda\) first. If the cut is scale-separated, a dynamics search for
quadrature is spent proving a kinematic identity.

**WEAVE isotropy from a 3D volume exponent.**
In the chain construction the graph metric in the window
\(\ell_W\ll r\ll S\ell_W\) is

\[
ds^2=dx^2+dy^2+\ell_W^2\,dz^2,
\qquad
\ell_W=\frac{1}{2\sqrt{\lambda}}.
\]

Volume growth can read \(3\) while the axis ratio is \(\ell_W\). Every
WOVEN ladder point \(\lambda\le 0.08\) has \(\ell_W\ge 1.77\). The isotropic
point \(\ell_W=1\) is \(\lambda=1/4\), stub fraction
\(1-e^{-1/2}\approx 0.39\), inside the preregistered OVERCONNECTED regime.
A WEAVE0-3D verdict is not an isotropy result. Detail:
`disorder-improves-isotropy/note.md`.

**\(H(z)\) from \(\dot\rho_S\) before a graph changes.**
Between structural events, \(G\) is fixed, \(Q\) is frozen, and
VACEXC0 says the carrier \(\delta\psi\) evolves independently of the
background. Packet arrival times are then constant. \(H=0\) until the
graph changes. The relation \(a\propto 1/\rho_S\) is the dilution identity
of comoving surfaces inside an expansion that was already assumed; it does
not determine \(\ddot a\). Detail: `dark-energy-weave/note.md`.

**Lorentz from the long-wave limit of \(H=-A\).**
J2 and J3 dispersions are separable sums of cosines. At the band bottom the
quartic polynomial has no \(q_i^2 q_j^2\) term. Rotational invariance of
the quartic symbol requires the cross coefficient to be twice the pure
coefficient. Both lattices give ratio \(0\), at the same order as the first
Lorentz-violating correction. Detail: `lorentz-emergent/note.md`.

---

## Also settled enough to change the queue

**Spontaneous splits of a uniform vacuum.** Continuity of the summed
amplitude forces \(\dot\mu=i(s+\sum_C\psi)\) with no dependence on the fiber
coordinate \(d\). A uniform nonzero state fails this on every cover.
STORE replays pass because they are the true predecessor. A jet search on
uniform vacuum cells should be empty except for the identity match. Detail:
`dynamical-jet-admissibility/note.md`.

**Structural lifetimes before radiative ones.** A motif with no eigenvalue
below \(-8\) on J2 (below \(-12\) on J3) decays by the earned unitary into
the band. The clique bound is \(m\ge n-9\) for an embedded \(K_n\), \(n\ge 10\).
Smaller motifs are not given a gap by that trial vector. Fitting a split
hazard to an in-band packet measures radiation. Detail:
`matter-stable-composite/note.md`, `lifetime-hazard/note.md`.

**Rewire branching ratios.** The tie is earned and exact principles do not
break it. A splitting \(\Delta E\) between the two re-pairings, on J3 or on
a weave, is the one number that would reopen a rate. A Monte Carlo of
outcomes does not.

## Order

1. Cut versus interior histogram of \(B/q\), with the three ensemble means
   as frozen controls and \(\lambda\) recorded per leg.
2. Only if the cut matches none of the three rows: ask which dynamics moves
   \(x\).
3. Weave: report the axis ratio \(\ell_W\) beside any \(d_{\mathrm{eff}}\).
   Do not read a passing 3D volume gate as isotropy.
4. Leave \(H(z)\) and a microscopic area fit until (1) and a real change in
   \(G\) exist. The coefficient they would be fitted to is already fixed by
   I1 if the channel count is \(k\) and \(\bar h=1\).
5. Spectral gap of candidate motifs before any decay campaign; jet
   continuity filter before any fiber-measure fit.
