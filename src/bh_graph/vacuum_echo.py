"""Phase-2 protocol C: echo null-check (mock-first, frozen statistic).

Prediction (T-o, `gwdata.echo_margin_orders`): NO detectable echoes —
echo energy ~1e-160 vs O(0.01) detectability, margin ~160 orders
(dimensional estimate, not a leg S-matrix derivation — T14).

Prereg (`docs/derivation-prereg.md` §3.2): mock-first with a FROZEN
excess-power statistic (must FIRE on detectable injected echoes, stay
QUIET at model level), then real-data leg: GWOSC 4 kHz strain for
GW150914 + GW190521 IF reachable, else PUBLISHED LVK nulls (O3
BayesWave + template searches) + analytic margin quote. Data leg
SKIPPED (not failed) with reason if GWOSC unreachable.

Constraints: NO Bilby PE without pre-approved budget. NO overtone
claims (D2-open). Verify LVK nulls stay consistent; quote the margin.
"""
from __future__ import annotations

import numpy as np

from bh_graph.gwdata import echo_margin_orders

# LVK published nulls (quoted, not re-derived): O3 echo searches found
# no significant evidence (p-values noise-consistent).
LVK_NULLS = (
    "Abbott et al. PRD 112, 084080 (O3 BayesWave echo search: null)",
    "Uchikata et al. PRD 108, 104040 (template echo search: null)",
)

__all__ = [
    "LVK_NULLS",
    "frozen_statistic",
    "mock_ringdown",
    "mock_validation",
    "null_verdict",
    "try_gwosc_fetch",
]


def mock_ringdown(fs_hz: float = 4096.0, dur_s: float = 2.0,
                  f0_hz: float = 150.0, tau_s: float = 0.01,
                  echo_delay_s: float = 0.3, echo_amp: float = 0.0,
                  seed: int = 0) -> dict:
    """Synthetic ringdown + noise + optional echo. {ok, t, h}.

    h = damped sinusoid + white noise + echo_amp-scaled repeat at
    echo_delay_s. echo_amp=0 → model-level (QUIET expected);
    echo_amp~0.3 → detectable (FIRE expected).
    """
    bad = {"ok": False}
    if not (np.isfinite(fs_hz) and fs_hz > 0 and np.isfinite(dur_s)
            and dur_s > 0 and np.isfinite(echo_amp) and echo_amp >= 0):
        return bad
    rng = np.random.default_rng(seed)
    n = int(fs_hz * dur_s)
    t = np.arange(n) / fs_hz
    h = (np.exp(-t / tau_s) * np.sin(2 * np.pi * f0_hz * t)
         + rng.normal(0.0, 0.05, size=n))
    if echo_amp > 0:
        k = int(echo_delay_s * fs_hz)
        if 0 < k < n:
            h[k:] += echo_amp * np.exp(-t[:n - k] / tau_s) * np.sin(
                2 * np.pi * f0_hz * t[:n - k])
    return {"ok": True, "t_s": t, "h": h, "fs_hz": float(fs_hz),
            "echo_delay_s": float(echo_delay_s), "echo_amp": float(echo_amp)}


def frozen_statistic(mock: dict, window_s: float = 0.02) -> dict:
    """FROZEN statistic: echo-window excess power / background.

    Signal window = [delay, delay+window]; background = late-time
    window of equal length. {ok, snr_excess}. Frozen = fixed here
    before any real-data comparison.

    NOTE (real-data limitation, found 2026-09-28, behavior unchanged):
    validated on WHITE-noise mocks only. On RAW colored strain the
    signal mean-square keeps the DC offset while the background
    VARIANCE removes it, so unwhitened DC (~1e-19) fires the statistic
    spuriously (GW150914/L1: 364; symmetric var/var post-hoc: < 5
    everywhere). Real-strain use is descriptive-only; the null verdict
    is margin-driven + LVK published nulls. See docs/VACUUM_REPORT.md.
    """
    bad = {"ok": False}
    if not mock.get("ok", False):
        return bad
    t, h = mock["t_s"], mock["h"]
    d = mock["echo_delay_s"]
    sig = h[(t >= d) & (t < d + window_s)]
    bkg = h[(t >= d + 4 * window_s) & (t < d + 5 * window_s)]
    if sig.size < 8 or bkg.size < 8:
        return bad
    bvar = float(np.var(bkg))
    if not (np.isfinite(bvar) and bvar > 0):
        return bad
    return {"ok": True,
            "snr_excess": float(np.mean(sig ** 2) / bvar - 1.0)}


def mock_validation() -> dict:
    """Statistic power: FIRES on detectable echo, QUIET at model level.

    {ok, snr_detectable, snr_model, fires, quiet}. Threshold 5.0
    (excess power ratio), fixed here.
    """
    m_det = mock_ringdown(echo_amp=0.5, seed=2)
    m_mod = mock_ringdown(echo_amp=0.0, seed=2)
    s_det = frozen_statistic(m_det)
    s_mod = frozen_statistic(m_mod)
    if not (s_det["ok"] and s_mod["ok"]):
        return {"ok": False}
    thresh = 5.0
    return {"ok": True, "snr_detectable": s_det["snr_excess"],
            "snr_model": s_mod["snr_excess"], "threshold": thresh,
            "fires": bool(s_det["snr_excess"] > thresh),
            "quiet": bool(s_mod["snr_excess"] < thresh)}


def try_gwosc_fetch() -> dict:
    """Attempt GWOSC 4 kHz fetch for GW150914/GW190521. {ok, reason}.

    ok=False with reason (missing package / no network / fetch error) →
    caller takes the published-nulls path (SKIPPED data leg, prereg §3.2).
    Never raises, never blocks long (short timeout).
    """
    try:
        import gwosc  # noqa: F401
    except ImportError:
        return {"ok": False,
                "reason": "gwosc-package-missing (published-nulls path)"}
    try:
        from gwosc.locate import get_event_urls
        urls = get_event_urls("GW150914", format="hdf5", sample_rate=4096)
        if not urls:
            return {"ok": False, "reason": "no-4kHz-URLs-listed"}
        return {"ok": True, "reason": "",
                "note": "URLs listed; strain download not attempted "
                        "(margin is analytic; see null_verdict)"}
    except Exception as exc:  # noqa: BLE001 -- any network/API failure routes to the published-nulls path by design
        return {"ok": False, "reason": f"gwosc-fetch-error: {exc}"}


def null_verdict() -> dict:
    """Analytic null verdict + margin quote. {verdict, margin_orders, ...}.

    Model predicts NO detectable echoes; PASS = prediction consistent
    with LVK published nulls (prediction far below detectability).
    """
    margin = float(echo_margin_orders())
    return {"verdict": "PASS" if margin > 10.0 else "FAIL",
            "margin_orders": margin,
            "detect_energy_ref": 0.01,
            "lvk_nulls": list(LVK_NULLS),
            "gwosc": try_gwosc_fetch()}
