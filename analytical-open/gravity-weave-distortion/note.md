# Weave distortion changes the anisotropic metric, not \(G_{\mu\nu}\) in vacuum form

A localized excess or deficit of stitches changes \(\ell_W(x)\) and
therefore the transverse coefficient in

\[
ds^2=dx^2+dy^2+\ell_W(x)^2\,dz^2
\]

(`disorder-improves-isotropy/note.md`). The curvature of this metric is
computable from \(\ell_W(x)\) by the usual formula for a diagonal metric.
It is not small just because the stitch perturbation is small: the
background itself is anisotropic by \(\ell_W\), which is \(\ge 1.77\) on
the WOVEN ladder. A "weak field around flat space" expansion is the wrong
linearization. The background is not \(\delta_{ab}\).

Linearized perturbations on top of that background fall into two classes.

- In-plane, at fixed \(\ell_W\): the J2 Hessian is nondegenerate, the
  static response is the Yukawa (or the excluded Laplace) problem of
  `gravity-structural-response/note.md`. Range \(O(1)\) or \(1/r\) only on
  the excluded edge.
- Transverse gradients of \(\ell_W\): these are changes of \(G\), forbidden
  between events. They are a different sector from \(\delta\psi\).

A numerical experiment that places a \(\psi\) packet on a weave and looks
for an isotropic \(1/r\) potential is aimed at a solution the metric does
not have. The observable the metric does have is a quadrupole aligned with
the sheet normal, scaling as the second derivatives of \(\ell_W\), present
only if the stitch field varies in space. If \(\ell_W\) is uniform, this
curvature vanishes and the packet propagates on the constant anisotropic
background. That null is the control. A nonzero isotropic potential on
that control is an estimator leak.
