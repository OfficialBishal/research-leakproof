"""Correlation reported without an error metric or a baseline to beat."""

from __future__ import annotations

import re

from .. import finding as f

CHECK = "metric_honesty"

CORRELATION = {"pearson", "spearman", "kendall", "r", "corr", "correlation", "rho", "auc", "auroc"}
ERROR_METRIC = {"r2", "rsquared", "squared", "mse", "rmse", "mae", "nrmse", "mape", "smape", "logloss"}
BASELINE_HINT = {"baseline", "skill", "naive", "control", "chance", "null", "vs"}


def _tokens(key) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", str(key).lower()) if t}


def run(ctx):
    if ctx.metrics is None:
        return None

    keys = list(ctx.metrics.keys()) if isinstance(ctx.metrics, dict) else list(ctx.metrics)
    token_sets = [_tokens(k) for k in keys]

    has_corr = any(t & CORRELATION for t in token_sets)
    has_error = any(t & ERROR_METRIC for t in token_sets)
    has_baseline = any(t & BASELINE_HINT for t in token_sets)

    evidence = {
        "reported": sorted(str(k).lower() for k in keys),
        "has_correlation": has_corr,
        "has_error_metric": has_error,
        "has_baseline": has_baseline,
    }

    if has_corr and not has_error:
        return f.warn(
            CHECK,
            "A correlation metric is reported without an error metric",
            "Correlation is scale-invariant: it can look strong while absolute error is large or the "
            "model loses to a trivial baseline. Pair it with R^2 / MSE.",
            evidence,
            fix="Report R^2 or (R)MSE next to the correlation, and a skill-vs-baseline comparison.",
        )
    if not has_baseline:
        return f.info(
            CHECK,
            "No baseline metric detected",
            "A score is only meaningful relative to a baseline (predicting the mean, last value, or "
            "majority class). Include one so readers can judge real skill.",
            evidence,
            fix="Add a baseline metric so improvement is measurable.",
        )
    return f.ok(CHECK, "Reported metrics include error and baseline context", evidence=evidence)
