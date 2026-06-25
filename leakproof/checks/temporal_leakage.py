"""Training timestamps that reach into or past the test period."""

from __future__ import annotations

import numpy as np

from .. import finding as f
from .._stats import as_1d

CHECK = "temporal_leakage"


def run(ctx):
    if ctx.time_train is None or ctx.time_test is None:
        return None

    train = as_1d(ctx.time_train)
    test = as_1d(ctx.time_test)
    if train.size == 0 or test.size == 0:
        return None

    test_start = test.min()
    n_after = int((train >= test_start).sum())
    frac = n_after / train.size

    evidence = {
        "train_range": [_fmt(train.min()), _fmt(train.max())],
        "test_range": [_fmt(test.min()), _fmt(test.max())],
        "n_train_at_or_after_test_start": n_after,
        "frac_train_after_test_start": round(frac, 4),
    }
    if n_after:
        return f.warn(
            CHECK,
            f"{n_after} training point(s) fall at or after the test period begins",
            "For a forecasting / time-ordered task this is look-ahead leakage: the model trains on "
            "information from the future it is asked to predict.",
            evidence,
            fix="Use a time-based split where every training timestamp precedes every test timestamp "
                "(add an embargo gap if samples are autocorrelated).",
        )
    return f.ok(CHECK, "Training period precedes the test period", evidence=evidence)


def _fmt(v):
    if isinstance(v, np.datetime64):
        return str(v)
    try:
        return round(float(v), 6)
    except (TypeError, ValueError):
        return str(v)
