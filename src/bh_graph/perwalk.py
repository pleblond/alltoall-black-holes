"""BG: Persistent walks with internal budgets (mass from hop accounting).

Three honest pieces, one negative result:

1. INTERNAL BUDGET (derived): hops have fixed length, split between
   translation and internal cycles (zitter): v^2 + r_clock^2 = c^2, so a
   clock moving at v ticks at sqrt(1-v^2) — time dilation by counting,
   no Lorentz postulates. Massless = all-translation limit. (Linear
   budget 1-v would be WRONG; quadrature is load-bearing and tested.)

2. DEGREE DRIFT (measured, negative result): target-degree-biased hopping
   (P ~ d_target, the entropic rule) on flux-conserved pileup d(r) =
   d_0 + A/r^2 gives drift ~ 1/r^3, NOT Newton 1/r^2. Heterogeneity alone
   cannot source gravity — the temperature factor in Appendix AS is
   load-bearing, not decorative. Getting 1/r^2 from pure graph statistics
   would need Coulomb-like (1/r) pileup, which flux conservation forbids.

3. PERSISTENCE + SPIN: heading memory mu raises trajectories from diffusive
   (MSD ~ t) toward ballistic (MSD ~ t^2); spin as internal circulation
   leaves mean drift unchanged to first order (effacement toy), and the
   Mathisson-Papapetrou fractional correction for Mercury (~1e-14) is
   computed and negligible — the user's spin question, quantified.
"""
from __future__ import annotations

import numpy as np


def clock_rate(speed: float, c: float = 1.0) -> float:
    """Internal-cycle rate at translation speed v: sqrt(1-v^2/c^2)."""
    return float(np.sqrt(max(1.0 - (speed / c) ** 2, 0.0)))


def max_speed(internal_frac: float, c: float = 1.0) -> float:
    """Translation speed given internal budget fraction: c*sqrt(1-f^2)... .

    Convention: f = internal cycles per tick as fraction of hop length;
    v^2 + (f c)^2 = c^2.
    """
    return float(c * np.sqrt(max(1.0 - internal_frac**2, 0.0)))


def degree_drift_1d(d_plus: float, d_minus: float) -> float:
    """Mean radial step for P ~ target degree: (d+ - d-)/(d+ + d-)."""
    return float((d_plus - d_minus) / max(d_plus + d_minus, 1e-300))


def pileup_degree(r, d0: float = 6.0, amp: float = 100.0):
    """Flux-conserved leg pileup around a mass: d(r) = d0 + A/r^2."""
    r = np.asarray(r, dtype=float)
    return d0 + amp / np.maximum(r, 1e-300) ** 2


def drift_profile(r_grid, d0: float = 6.0, amp: float = 100.0, dr: float = 0.5):
    """Measured mean inward step vs r on the pileup profile."""
    out = []
    for r in np.asarray(list(r_grid), dtype=float):
        out.append(-degree_drift_1d(pileup_degree(r + dr, d0, amp),
                                    pileup_degree(r - dr, d0, amp)))
    return np.array(out)  # positive = inward


def drift_power_law(r_grid=(20.0, 40.0, 80.0, 160.0)) -> float:
    """Log-log slope of drift vs r (heterogeneity alone: expect ~ -3)."""
    r = np.asarray(list(r_grid), dtype=float)
    d = drift_profile(r)
    slope, _ = np.polyfit(np.log(r), np.log(np.maximum(d, 1e-300)), 1)
    return float(slope)


def generalized_drift(r_grid, response, d0: float = 6.0, amp: float = 100.0,
                      dr: float = 0.5):
    """BP no-go: drift for hop weights w = response(local degree).

    Any local rule sees only d(r); drift ~= (w'-form) x d'(r) ~ g(d)/r^3.
    """
    out = []
    for r in np.asarray(list(r_grid), dtype=float):
        w_plus = response(pileup_degree(r + dr, d0, amp))
        w_minus = response(pileup_degree(r - dr, d0, amp))
        out.append(-degree_drift_1d(w_plus, w_minus))
    return np.array(out)


def nogo_slopes(r_grid=(20.0, 40.0, 80.0, 160.0, 320.0)) -> dict:
    """BP: drift slopes for natural rules (all ~ -3) + the absurd escape (~ -2).

    Background d -> d0 kills every smooth weight rule; only the
    background-subtracted exp-root monstrosity escapes — documenting that
    weight-rules cannot honestly reach -2.
    """
    import math
    rules = {
        "linear": lambda d: d,
        "sqrt": lambda d: math.sqrt(max(d, 1e-300)),
        "saturated": lambda d: d / (1.0 + d),
        "tuned_exp_root": lambda d: math.exp(2.0 * math.sqrt(max(d, 1e-300))),
        "absurd_bg_sub": lambda d: math.exp(2.0 * math.sqrt(max(d - 6.0, 1e-9))),
    }
    out = {}
    for name, fn in rules.items():
        vec = np.vectorize(fn)
        d = generalized_drift(r_grid, vec)
        r = np.asarray(list(r_grid), dtype=float)
        slope, _ = np.polyfit(np.log(r), np.log(np.maximum(d, 1e-300)), 1)
        out[name] = float(slope)
    return out


def mu_of_chi(r, c: float = 1.0, d0: float = 6.0, amp: float = 100.0):
    """BP: persistence from LOCAL leg-density fluctuations: 1 - mu = c*sqrt(chi).

    chi = (d(r) - d0)/amp ~ 1/r^2; walker sees density, never r directly.
    LABELED ASSUMPTION (fluctuation story, not derived): the unique honest
    escape from the no-go, joining the micro-derivation queue with BH's 1/2.
    """
    r = np.asarray(r, dtype=float)
    chi = np.maximum((pileup_degree(r, d0, amp) - d0) / amp, 0.0)
    return np.clip(1.0 - c * np.sqrt(chi), 0.0, 0.999)


def much_slope_analytic(r_grid=(10.0, 20.0, 40.0, 80.0, 160.0),
                        c: float = 1.0) -> float:
    """BP: exact slope of v(r) = b(r)/(1 - mu(r)) — the escape, analytic."""
    r = np.asarray(list(r_grid), dtype=float)
    b = np.array([-degree_drift_1d(pileup_degree(x + 0.5), pileup_degree(x - 0.5))
                  for x in r])
    v = b / (1.0 - mu_of_chi(r, c))
    slope, _ = np.polyfit(np.log(r), np.log(np.maximum(v, 1e-300)), 1)
    return float(slope)


def amplification_check(r: float = 10.0, mu: float = 0.9, n_walkers: int = 400,
                        n_steps: int = 4000, seed: int = 0) -> dict:
    """BP: validate v = b/(1-mu) by 1D persistent-walk simulation (small r)."""
    rng = np.random.default_rng(seed)
    b = -degree_drift_1d(pileup_degree(r + 0.5), pileup_degree(r - 0.5))
    head = rng.choice([-1.0, 1.0], size=n_walkers)
    tot = np.zeros(n_walkers)
    for _ in range(n_steps):
        p_keep = (1.0 + mu) / 2.0 + 0.5 * b * head
        keep = rng.random(n_walkers) < np.clip(p_keep, 0.0, 1.0)
        head = np.where(keep, head, -head)
        tot += head
    measured = float(tot.mean() / n_steps)
    return {"measured": measured, "predicted": float(b / (1.0 - mu)), "bias": b}


def persistent_walk(n_steps: int = 2000, mu: float = 0.9, bias: float = 0.0,
                    seed: int = 0) -> np.ndarray:
    """2D heading-memory walk; returns trajectory. bias = inward pull/step."""
    rng = np.random.default_rng(seed)
    pos = np.zeros(2)
    head = np.array([1.0, 0.0])
    traj = [pos.copy()]
    for _ in range(n_steps):
        inward = -pos / max(np.linalg.norm(pos), 1e-9)
        want = (1 - mu) * (rng.normal(size=2) * 0.5 + bias * inward) + mu * head
        nrm = np.linalg.norm(want)
        head = want / max(nrm, 1e-300) if nrm > 1e-12 else head
        pos = pos + head
        traj.append(pos.copy())
    return np.array(traj)


def msd_exponent(traj: np.ndarray) -> float:
    """Log-log slope of MSD vs t (1 = diffusive, 2 = ballistic)."""
    d2 = np.sum((traj - traj[0]) ** 2, axis=1)
    t = np.arange(1, len(d2))
    slope, _ = np.polyfit(np.log(t[len(t)//4:]), np.log(np.maximum(d2[1:][len(t)//4:], 1e-300)), 1)
    return float(slope)


def spin_circulation_drift(n_steps: int = 2000, spin: float = 0.0, bias: float = 0.02,
                           seed: int = 0) -> np.ndarray:
    """Mean displacement of a walker with internal circulation bias.

    Spin adds a perpendicular rotational component to each hop (Magnus-like);
    mean radial drift must match the spinless case to first order
    (effacement toy): circulation averages out over full turns.
    """
    rng = np.random.default_rng(seed)
    pos = np.array([50.0, 0.0])
    phase = 0.0
    for _ in range(n_steps):
        inward = -pos / max(np.linalg.norm(pos), 1e-9)
        perp = np.array([-inward[1], inward[0]])
        phase += spin
        step = 0.05 * inward + 0.02 * rng.normal(size=2) + spin * 0.1 * (
            np.cos(phase) * perp + np.sin(phase) * inward)
        pos = pos + step
    return pos


def mpd_fractional(m_planck: float = 9.14e37, r_planck: float = 2.85e45,
                    chi: float = 40.0) -> float:
    """Mathisson-Papapetrou/Newton ~ chi (M/r)^2 (Mercury defaults: Sun, perihelion)."""
    return float(chi * (m_planck / max(r_planck, 1e-300)) ** 2)
