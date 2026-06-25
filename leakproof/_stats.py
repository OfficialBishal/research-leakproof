"""Small numeric helpers shared across checks. NumPy is the only dependency."""

from __future__ import annotations

import math

import numpy as np

# Standard normal quantiles, hard-coded so we don't pull in SciPy.
Z_ALPHA_TWO_SIDED_05 = 1.959963984540054   # P(|Z| < z) = 0.95
Z_POWER_80 = 0.8416212335729143            # P(Z < z) = 0.80


def as_2d(x) -> np.ndarray:
    """Coerce any array-like (list, Series, DataFrame, ndarray) to a 2-D array."""
    arr = np.asarray(x)
    if arr.ndim == 0:
        arr = arr.reshape(1, 1)
    elif arr.ndim == 1:
        arr = arr.reshape(-1, 1)
    return arr


def as_1d(x) -> np.ndarray:
    return np.asarray(x).ravel()


def row_hashes(x) -> list[bytes]:
    """Content hash per row, so identical rows collide regardless of index."""
    arr = as_2d(x)
    out = []
    for row in arr:
        out.append(np.ascontiguousarray(row).tobytes())
    return out


def pearson(a, b) -> float:
    a = as_1d(a).astype(float)
    b = as_1d(b).astype(float)
    n = min(a.size, b.size)
    if n < 2:
        return float("nan")
    a, b = a[:n], b[:n]
    mask = np.isfinite(a) & np.isfinite(b)
    if mask.sum() < 2:
        return float("nan")
    a, b = a[mask], b[mask]
    a = a - a.mean()
    b = b - b.mean()
    denom = math.sqrt(float((a * a).sum()) * float((b * b).sum()))
    if denom == 0.0:
        return float("nan")
    return float((a * b).sum() / denom)


def mde_correlation(n: int, power: float = 0.80, alpha: float = 0.05) -> float:
    """Minimum correlation detectable at the given power via the Fisher-z normal approximation."""
    if n is None or n <= 3:
        return float("nan")
    z_alpha = Z_ALPHA_TWO_SIDED_05 if alpha == 0.05 else _z_two_sided(alpha)
    z_beta = Z_POWER_80 if power == 0.80 else _z_one_sided(power)
    z = (z_alpha + z_beta) / math.sqrt(n - 3)
    return math.tanh(z)


def _z_two_sided(alpha: float) -> float:
    return _inv_norm(1.0 - alpha / 2.0)


def _z_one_sided(p: float) -> float:
    return _inv_norm(p)


def _inv_norm(p: float) -> float:
    """Acklam's rational approximation to the standard-normal inverse CDF."""
    if not 0.0 < p < 1.0:
        return float("nan")
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
            ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
