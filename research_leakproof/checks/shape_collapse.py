"""A high overall correlation that hides near-zero per-unit signal.

The classic failure: a model learns the ranking of units (their means) but predicts almost no
variation *within* a unit. Aggregate correlation looks strong; per-unit skill is ~zero.
"""

from __future__ import annotations

import numpy as np

from .. import finding as f
from .._stats import as_1d, pearson

CHECK = "shape_collapse"


def run(ctx):
    if ctx.predictions is None or ctx.targets is None:
        return None

    preds = as_1d(ctx.predictions).astype(float)
    targets = as_1d(ctx.targets).astype(float)
    n = min(preds.size, targets.size)
    preds, targets = preds[:n], targets[:n]

    agg_r = pearson(preds, targets)
    pred_std = float(np.nanstd(preds))
    target_std = float(np.nanstd(targets))
    std_ratio = pred_std / target_std if target_std else float("nan")

    evidence = {
        "aggregate_pearson_r": _round(agg_r),
        "pred_std_over_target_std": _round(std_ratio),
    }

    agg_threshold = ctx.option("shape_collapse_agg_r", 0.30)
    within_threshold = ctx.option("shape_collapse_within_r", 0.10)
    flat_ratio = ctx.option("shape_collapse_flat_ratio", 0.05)

    # With units we can separate between-unit means from within-unit shape.
    if ctx.units is not None:
        units = as_1d(ctx.units)[:n]
        _, inv = np.unique(units, return_inverse=True)
        counts = np.bincount(inv).astype(float)
        pred_unit_mean = np.bincount(inv, weights=preds) / counts
        target_unit_mean = np.bincount(inv, weights=targets) / counts

        # Residuals after removing each unit's mean = the within-unit variation.
        pr = preds - pred_unit_mean[inv]
        tr = targets - target_unit_mean[inv]
        within_target_var = float(np.mean(tr * tr))
        within_pred_var = float(np.mean(pr * pr))
        # How much the prediction moves within a unit, relative to how much the target does.
        within_move = (within_pred_var / within_target_var) ** 0.5 if within_target_var > 0 else float("nan")
        within_r = pearson(pr, tr) if within_pred_var > 0 and within_target_var > 0 else float("nan")

        evidence["within_unit_r"] = _round(within_r)
        evidence["within_unit_movement_ratio"] = _round(within_move)

        collapsed = (
            np.isfinite(within_move) and within_move < flat_ratio
        ) or (
            np.isfinite(within_r) and within_r < within_threshold
        )
        if np.isfinite(agg_r) and agg_r >= agg_threshold and np.isfinite(within_target_var) \
                and within_target_var > 0 and collapsed:
            return f.error(
                CHECK,
                f"Aggregate r={agg_r:.2f}, but predictions barely vary within a unit",
                "The overall correlation is carried by differences between unit means, not by "
                "predicting variation inside each unit. The model has learned the ranking of units, "
                "not their shape.",
                evidence,
                fix="Score within-unit correlation (and R^2/MSE) alongside the aggregate, and compare "
                    "against a baseline that predicts each unit's mean.",
            )

    # Without units, the visible failure mode is a near-constant prediction.
    if np.isfinite(std_ratio) and std_ratio < flat_ratio:
        return f.warn(
            CHECK,
            f"Predictions are nearly constant (std is {std_ratio:.1%} of the target's)",
            "A model that barely varies its output can still post a non-trivial aggregate metric "
            "while having no real resolving power.",
            evidence,
            fix="Check per-unit/per-sample variance and compare against a constant-mean baseline.",
        )

    return f.ok(CHECK, "Predictions vary and track targets beyond unit means", evidence=evidence)


def _round(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if not np.isfinite(v) else round(v, 4)
