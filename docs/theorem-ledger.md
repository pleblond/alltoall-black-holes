# Theorem Ledger

The earned mathematical spine of the model: exact algebraic theorems,
banked derivations, and empirically established laws — kept separate
from campaign verdicts (`docs/scaffolding-history.md`, `docs/DEFERRED.md`)
and from physical hypotheses (`docs/hypothesis-ledger.md`). Status words:

- **Exact** — follows algebraically from stated premises; no numerics load-bearing.
- **Exact / banked** — exact, with the derivation pinned by tests/records.
- **Exact / \<CAMPAIGN\>** — proved inside the named campaign's frozen apparatus.
- **Derived** — established by campaign measurement under frozen gates.
- **Candidate / analytic implication** — precise statement filed, not yet earned.

Two ledger entries cite work not yet merged at ledger creation: §9
(BHQREL0-MEASURE-DEBT — no `bhqrel` records in repo) and §13
(CROSS-IMPL-B — no `analytical-open` note beyond
`cross-implications.tex` in repo). CROSS-IMPL-A is merged
(`docs/crossa-verdict.md`, PR #153); §7 records its verdict. They are
transcribed as filed, with their unbanked status explicit. Ledger entries never promote anything
by themselves; promotion happens only through the cited campaign or
banking record.

---

## 1. Fundamental graph-field dynamics

| Theorem / law | Statement | Status |
|---|---|---|
| **Fixed-\(G\) unitarity** | \(U_G(t)=e^{-iH_Gt}\); norm-preserving reversible evolution on fixed graph | **Exact** |
| **Time reversal** | \(\Theta U(t)\Theta^{-1}=U(-t)\) under the real-Hamiltonian convention | **Exact** |
| **Physical quotient** | Raw labels/global \(U(1)\) contain redundancies; observables live on the earned quotient | **Exact / banked** |
| **Fixed-\(G\) continuation** | Tested fixed-\(G\) evolution remains valid indefinitely; structural change is not forced by unitary evolution | **EVENT0 derived** |
| **No jet event surface** | No nontrivial finite-Krylov dynamical-equivalence surface exists on tested ontology | **JET1-NULL** |

## 2. Hidden / vacuum sector

| Theorem / law | Statement | Status |
|---|---|---|
| **Hidden-sector separation** | \(P_-\) supports physical relational information invisible to selected transport channels | **Derived** |
| **Hidden vacuum family** | Nonzero JOINT orientations can differ while remaining exactly vacuum-like | **Derived** |
| **Vacuum texture null dynamics** | Spatial hidden orientation gradients can be relationally real while \(H\psi=E=w_{\rm sym}=0\) | **Derived** |
| **Vacuum robustness** | Protected small perturbations remain bounded over long tested evolution | **Derived** |
| **Hidden sign reversal** | Hidden-sector changes can reverse structural/accounting response while matched coarse quantities remain fixed | **Derived** |

## 3. Merge / split / information

One of the strongest theorem blocks.

| Theorem | Statement | Status |
|---|---|---|
| **Merge uniqueness** | Given a selected edge, the contraction update is unique and covariant | **Exact / MERGE0** |
| **Split fiber** | Reduced merged state has continuous inverse freedom; generic continuous fiber dimension \(=2\) real | **Exact / SPLIT0** |
| **Split decomposition** | \(\displaystyle p=(s+d)/2,\ q=(s-d)/2\) | **Exact** |
| **Complete inverse coordinate** | \(\xi=(c,d)\), with discrete cover \(c\) and complex relative mode \(d\) | **Exact / minimal** |
| **STORE reversibility** | Enlarging the state with \(Q\supset\xi\) makes merge/split exactly reversible | **STORE0 exact** |
| **Conditional split determinism** | Given complete \(Q\), inverse split products are unique | **Exact** |
| **Reduced split underdetermination** | Without \(Q\), multiple inverse states remain | **Exact** |
| **\(Q\) frozen between events** | \(Q\) does not evolve under tested fixed-\(G\) evolution | **QDYN0B** |
| **Event-local accounting** | \(R=F_R(M,Q)\) is a current-event functional, not persistent stored energy | **QDYN0B** |
| **Current-account reversal** | Merge/split accounts reverse under the exact inverse operation | **Exact / banked** |

## 4. Reservoir theorem

For the relative mode \(d\) and exclusive-neighborhood field \(W\):

\[
\boxed{i\dot d=d+W.}
\]

The merge account is

\[
\boxed{
R=A_0+\frac{|d|^2}{2}+\Re(\bar dW).
}
\]

Equivalently,

\[
\boxed{
R=\frac12|\dot d|^2+\frac12\Delta,
\qquad
\Delta=2A_0-|W|^2.
}
\]

And:

\[
\boxed{R_{\rm split}=-R_{\rm merge}.}
\]

Status: **exact / RESERVOIR0-XI**.

## 5. Qubit / STORE information theorem

For

\[
s=\psi_i+\psi_j,\qquad d=\psi_i-\psi_j,
\]

the norm decomposes exactly:

\[
\boxed{
|\psi_i|^2+|\psi_j|^2
=
\frac{|s|^2+|d|^2}{2}.
}
\]

Define

\[
P_-=\frac{|d|^2}{|s|^2+|d|^2}.
\]

QINFO proved this is exactly the previously banked qubit/two-level variable, with information

\[
\boxed{
S_Q=h_2(P_-).
}
\]

Status:

\[
\boxed{\text{QINFO0-IDENTICAL}}.
\]

Important corollary:

\[
d\in\mathbb C
\]

means **two real coordinates of one complex amplitude**, not two bits.

## 6. \(B\)-information theorem

With

\[
q=|\psi_i|^2+|\psi_j|^2,
\qquad
B=\Re(\bar\psi_i\psi_j),
\]

derived exactly:

\[
|s|^2=q+2B,
\qquad
|d|^2=q-2B.
\]

Therefore

\[
\boxed{
P_-=\frac12-\frac{B}{q}.
}
\]

Hence:

\[
\boxed{
S_Q
=
h_2\left(\frac12-\frac{B}{q}\right).
}
\]

And consequently:

\[
\boxed{
B=0
\iff
P_-=\frac12
\iff
S_Q=1\ {\rm bit}.
}
\]

So a \(B\)-null bond is a **maximally informative isolated \(Q\) channel**.

Near \(B=0\):

\[
\boxed{
1-S_Q
=
\frac{2}{\ln2}
\left(\frac{B}{q}\right)^2
+
O\left((B/q)^4\right).
}
\]

No linear information deficit exists.

## 7. Amplitude-phase factorization

Writing

\[
\psi_i=a_ie^{i\theta_i},
\qquad
\psi_j=a_je^{i\theta_j},
\]

define

\[
r=
\frac{2a_ia_j}{a_i^2+a_j^2},
\qquad
c=\cos(\Delta\theta).
\]

Then:

\[
\boxed{
\frac{2B}{q}=rc.
}
\]

With

\[
\lambda=\frac{a_i}{a_j},
\]

\[
\boxed{
r=\frac{2\lambda}{1+\lambda^2}
=\operatorname{sech}(\log\lambda).
}
\]

Therefore \(B/q\to0\) can result from either:

\[
\boxed{\text{phase quadrature }c\to0}
\]

or

\[
\boxed{\text{amplitude separation }r\to0},
\]

or both.

CROSS-IMPL-A resolved which mechanism BHQAREA0 actually realizes:
**amplitude hierarchy, not quadrature** (CROSSA-SCALE, 11/11).
\(R_2=\langle r^2\rangle\) collapses \(0.347\to1.3\times10^{-5}\) (ZERO
track) while \(C_2=\langle\cos^2\Delta\theta\rangle=1\) throughout
(NONZERO track) — the Perron ground state is real-positive, so the
boundary amplitudes are **in phase**, the opposite of quadrature. The
factorization reads

\[
\frac{2B}{q}
=
\underbrace{\operatorname{sech}(\log\lambda)}_{\rightarrow0}
\underbrace{\cos\Delta\theta}_{=1},
\]

with the hierarchy \(|\psi_{\rm core}|:|\psi_{\rm ext}|\) growing
\(\sim3{:}1\to518{:}1\) (median \(|\log\lambda|\): \(1.15\to6.25\)).
The controls select the mechanism doubly: patterns give
\(R_2=C_2=X_2=1\) with \(S=0\) exactly, while plain J3 keeps
\(R_2\to0.94\) with \(\bar h\approx0.10\) — MAX is selected by the
high-connectivity core plus its state, not by phases or J3 geometry
alone. The BH mechanism chain is therefore

\[
\boxed{
\text{highly connected core}
\rightarrow
\text{ground-state amplitude concentration}
\rightarrow
\text{core/exterior scale separation}
\rightarrow
P_-\to\frac12
\rightarrow
1\text{ bit/channel}
\rightarrow
S_Q^\partial\propto A.
}
\]

The exact \(B=0\iff S_Q=1\) (§6) stands unchanged; the empirically
established asymptotic route on the BH-like boundary is

\[
\boxed{
\lambda\to0\text{ or }\infty
\Rightarrow
r\to0
\Rightarrow
B/q\to0,
}
\]

with \(c=1\), rather than a quadrature condition. The area-law
information emerges from localization/amplitude contrast across the
interface. (No causal claim about BH formation; no follow-up campaign
opened to force any interpretation.)

## 8. BH boundary information area law

BHQAREA0 established:

\[
\boxed{
S_Q^\partial
=
\sum_{e\in\partial}
h_2\left(\frac12-\frac{B_e}{q_e}\right).
}
\]

For the BH-like all-to-all core in J3:

\[
\boxed{
S_Q^\partial
=
\kappa_*A+o(A)
}
\]

with

\[
\kappa_*=4.2207,
\]

\[
\sigma_*=4.2208,
\]

and

\[
\boxed{h_*=0.999990}.
\]

Thus:

\[
\boxed{\kappa_*=\sigma_*h_*}
\]

and the boundary is essentially maximally informative per isolated channel.

Status:

\[
\boxed{\text{BHQAREA0-MAX}}.
\]

This is a **derived information area law**, not yet thermodynamic BH entropy.

## 9. Boundary-correlation theorem/debt

Boundary \(Q\) channels are not independent. Pairwise covariance shows strong structured local coherence, with disjoint pairs diluting toward zero.

But:

\[
\boxed{\text{no earned joint }Q_\partial\text{ probability/state exists yet}.}
\]

Therefore:

\[
H(Q_\partial)
\]

and

\[
\mathcal T_\partial
=
\sum_eH(Q_e)-H(Q_\partial)
\]

are presently undefined within the earned ontology.

Status:

\[
\boxed{\text{BHQREL0-MEASURE-DEBT}}.
\]

An important **negative theorem/debt boundary**: the marginals do not determine the joint.
(BHQREL0 campaign not merged at ledger creation; entry transcribes the filed status.)

## 10. Dimension theorems

| Result | Statement | Status |
|---|---|---|
| **J2 operational dimension** | J2 belongs to a 2D geometric/transport class | **Derived** |
| **J3 operational dimension** | J3 is geometrically 3D | **DIM3/DIM31 derived** |
| **J3/cubic equivalence** | Many geometric/static channels agree with cubic 3D, though finite-size wavefront transfer is not exactly universal | **Derived** |
| **Dimension universality** | Microscopic lattice identity is not required for the same macroscopic dimension | **Derived / partial** |
| **Random-stitch non-theorem** | 3D volume growth does not imply 3D spectral dimension | **WEAVE0 derived counterexample** |

The last one in particular:

\[
\boxed{
d_H\simeq3
\not\Rightarrow
d_s\simeq3.
}
\]

## 11. WEAVE transverse-scale result

For the analyzed chain-weave architecture, the cross-implication note derives a transverse scale of the form

\[
\boxed{
\ell_W=\frac{1}{2\sqrt{\lambda}}
}
\]

with coarse anisotropic metric

\[
\boxed{
ds^2
=
dx^2+dy^2+\ell_W^2dz^2.
}
\]

This gives a mathematical explanation for why metric volume can look 3D while transport remains anisotropic.

Current mark: **analytic implication / awaiting dedicated theorem banking**, rather than fully banked theorem.

## 12. Event-law negative theorems

\[
\boxed{\text{TRIGGER0}}
\]

Existing candidate conditions do not imply firing.

\[
\boxed{\text{EVENT0}}
\]

Fixed-\(G\) evolution never requires structural departure; structural equivalences do not imply firing.

\[
\boxed{\text{JET1-NULL}}
\]

No nontrivial dynamical-jet equivalence surface exists on the tested ontology.

Thus:

\[
\boxed{
\text{event occurrence is not presently derivable from local instantaneous or finite-jet equivalence.}
}
\]

TIME-Q-0 is testing the remaining global/two-boundary route.

## 13. Two-stitch dimensional binding theorem — pending CROSS-IMPL-B

**Not banked yet**: a precise theorem candidate (CROSS-IMPL-B note not in repo at ledger creation).

For J2, expected:

\[
\boxed{
t_c^{J2}(r)=0
\quad\forall r\neq0.
}
\]

Divergent channel:

\[
\boxed{
|t|\ln\frac1{E-8}
\rightarrow8\pi\sqrt2
}
\]

independent of fixed separation.

Cancelled channel:

\[
\boxed{
t^2\ln\frac1{E-8}
\rightarrow
\frac{16\pi}{\lambda_\infty(r)},
}
\]

with

\[
\lambda_\infty(r)>\frac1{16}.
\]

Nearest neighbor:

\[
\boxed{\lambda_\infty=\frac18}.
\]

For J3, expected separation-uniform exclusion:

\[
\boxed{
|t|\le\frac{24}{\sqrt{55}}
\Rightarrow
\text{no out-of-band state}.
}
\]

And for adjacent J3 stitches, the sharper theorem candidate:

\[
\boxed{
|t|\le\sqrt{\frac{128}{11}}
}
\]

with exact edge combinations

\[
\boxed{\frac1{12},\qquad\frac I4}.
\]

Status: **theorem candidate currently assigned to CROSS-IMPL-B**, not yet earned.

---

## The compact core

The strongest mathematical spine of the current model:

\[
\boxed{
\begin{gathered}
i\dot\psi=H_G\psi,\\
(G,\psi,Q)\text{ is reversibly sufficient for merge/split},\\
Q\supset(c,d),\qquad i\dot d=d+W,\\
P_-=\frac12-\frac{B}{q},\\
S_Q=h_2(P_-),\\
B=0\iff S_Q=1,\\
S_Q^\partial\propto A\quad\text{for the BH-like J3 boundary},\\
J2\sim2D,\qquad J3\sim3D,\\
\text{fixed-}G\text{ dynamics does not itself supply the event law}.
\end{gathered}}
\]
