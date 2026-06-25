"""A self-contained leaky experiment, so `research-leakproof demo` shows the tool finding real problems."""

from __future__ import annotations

import numpy as np

from .audit import audit


def make_report():
    rng = np.random.default_rng(0)

    # 30 units, 8 timepoints each. Each unit has its own mean plus a within-unit shape.
    n_units, t = 30, 8
    unit_mean = rng.normal(size=n_units)
    units = np.repeat(np.arange(n_units), t)
    shape = np.sin(np.linspace(0, 3.14, t))
    targets = unit_mean[units] + 0.6 * np.tile(shape, n_units) + 0.1 * rng.normal(size=n_units * t)

    # A model that predicts each unit's mean: high aggregate r, no within-unit signal.
    predictions = unit_mean[units]

    # A row-level split that shares two rows and one whole unit between sides.
    feats = np.column_stack([targets, units])
    X_train = feats[:200]
    X_test = np.vstack([feats[200:], feats[:2]])   # last rows plus two duplicated train rows

    return audit(
        X_train=X_train,
        X_test=X_test,
        groups_train=units[:200],
        groups_test=np.concatenate([units[200:], units[:2]]),
        time_train=np.arange(200),
        time_test=np.arange(190, 240),             # overlaps the train period
        groups=units,                              # 240 rows, 30 independent units
        predictions=predictions,
        targets=targets,
        units=units,
        metrics={"pearson_r": 0.81},               # correlation only, no error metric
        n_test=42,
        effect_size=0.1,                           # below the detectable floor at n=42
        n_comparisons=12,
        corrected=False,
    )


def main():
    print(make_report().to_text())


if __name__ == "__main__":
    main()
