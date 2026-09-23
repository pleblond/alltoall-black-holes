"""W: Spin-aware area theorem from GW150914 posterior samples (public data).

Upgrades Appendix Q (Schwarzschild medians) to per-sample Kerr areas from the
GWOSC GWTC-1 posterior file (Overall_posterior, 8350 samples): component
dimensionless aligned spins chi_z = spin*costilt give exact Kerr areas, source
masses via Planck15 dL->z inversion (Hogg 1999 integral, grid-interpolated --
no astropy needed), and the remnant from published Mf/af Gaussians
(Isi et al. 2021 style: Mf = 63.1 +- 1.5 M_sun, af = 0.68 +- 0.06).

Output: full posterior of created legs dk = kf - k1 - k2 with P(dk > 0).
Figure generation falls back to medians if the HDF5 is absent; the file is
cached under data/ (6.8 MB, DOI 10.7935/82H3-HH23).
"""
from __future__ import annotations

from pathlib import Path
import urllib.request
import numpy as np

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
GW150914_URL = "https://dcc.ligo.org/public/0157/P1800370/005/GW150914_GWTC-1.hdf5"
GW150914_FILE = DATA_DIR / "GW150914_GWTC-1.hdf5"

# Planck15-ish flat LCDM
H0_KM_S_MPC = 67.7
OM_M = 0.307
C_KM_S = 299792.458
G_MSUN_M = 1477.0  # G M_sun / c^2 in meters
LP_M = 1.616255e-35
M2_PER_GMSUN2 = G_MSUN_M**2 / LP_M**2  # legs per (G M_sun/c^2)^2 area unit


def _e_z(z):
    return np.sqrt(OM_M * (1 + z) ** 3 + (1 - OM_M))


def dl_grid(zmax: float = 1.0, n: int = 2000) -> tuple[np.ndarray, np.ndarray]:
    z = np.linspace(0, zmax, n)
    dz = z[1] - z[0]
    integ = np.concatenate([[0], np.cumsum(0.5 * (_e_z(z[:-1]) ** -1 + _e_z(z[1:]) ** -1)) * dz])
    dl = (1 + z) * C_KM_S / H0_KM_S_MPC * integ
    return dl, z


_DL_GRID, _Z_GRID = dl_grid()


def z_from_dl(dl_mpc) -> np.ndarray | float:
    return np.interp(np.asarray(dl_mpc, dtype=float), _DL_GRID, _Z_GRID)


def kerr_legs_msun(m_msun, chi) -> np.ndarray | float:
    """Kerr exterior legs k = A/lp^2, A = 8 pi M (M + sqrt(M^2 - a^2))."""
    m = np.asarray(m_msun, dtype=float)
    a = np.clip(np.asarray(chi, dtype=float), -1, 1) * m
    area = 8.0 * np.pi * m * (m + np.sqrt(np.maximum(m**2 - a**2, 0.0)))
    return area * M2_PER_GMSUN2


def ensure_posteriors(path: Path = GW150914_FILE, timeout: float = 120.0) -> Path:
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(GW150914_URL, path)
    return path


def load_overall_posterior(path: Path = GW150914_FILE) -> dict[str, np.ndarray]:
    import h5py

    with h5py.File(path, "r") as f:
        s = f["Overall_posterior"][:]
    return {k: np.asarray(s[k], dtype=float) for k in s.dtype.names}


def source_masses_and_spins(post: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    z = z_from_dl(post["luminosity_distance_Mpc"])
    return {
        "m1": post["m1_detector_frame_Msun"] / (1 + z),
        "m2": post["m2_detector_frame_Msun"] / (1 + z),
        "chi1": post["spin1"] * post["costilt1"],
        "chi2": post["spin2"] * post["costilt2"],
        "z": z,
    }


def delta_legs_posterior(
    src: dict[str, np.ndarray],
    mf_mean: float = 63.1, mf_std: float = 1.5,
    af_mean: float = 0.68, af_std: float = 0.06, seed: int = 0,
) -> dict[str, np.ndarray | float]:
    """Per-sample created legs with remnant Gaussians (Kerr both ends)."""
    rng = np.random.default_rng(seed)
    n = len(src["m1"])
    k1 = kerr_legs_msun(src["m1"], src["chi1"])
    k2 = kerr_legs_msun(src["m2"], src["chi2"])
    mf = rng.normal(mf_mean, mf_std, n)
    af = np.clip(rng.normal(af_mean, af_std, n), 0, 0.998)
    kf = kerr_legs_msun(np.maximum(mf, 1.0), af)
    dk = kf - k1 - k2
    return {
        "dk": dk, "k1": k1, "k2": k2, "kf": kf,
        "median_frac": float(np.median(dk / (k1 + k2))),
        "p_positive": float(np.mean(dk > 0)),
    }


def median_analysis() -> dict[str, float]:
    """Fallback without HDF5: published medians, Kerr both ends."""
    k1 = float(kerr_legs_msun(35.6, 0.0))
    k2 = float(kerr_legs_msun(30.6, 0.0))
    kf = float(kerr_legs_msun(63.1, 0.68))
    dk = kf - k1 - k2
    return {"k1": k1, "k2": k2, "kf": kf, "dk": dk, "frac": dk / (k1 + k2)}
