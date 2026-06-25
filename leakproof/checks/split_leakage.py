"""Identical rows shared between the train and test splits."""

from __future__ import annotations

from .. import finding as f
from .._stats import row_hashes

CHECK = "split_leakage"


def run(ctx):
    if ctx.X_train is None or ctx.X_test is None:
        return None

    train = row_hashes(ctx.X_train)
    test = row_hashes(ctx.X_test)
    train_set = set(train)
    leaked = [i for i, h in enumerate(test) if h in train_set]
    n_test = len(test)
    n_leaked = len(leaked)
    frac = n_leaked / n_test if n_test else 0.0

    evidence = {
        "n_test": n_test,
        "n_train": len(train),
        "n_leaked_rows": n_leaked,
        "frac_test_leaked": round(frac, 4),
        "example_test_indices": leaked[:10],
    }
    if n_leaked:
        return f.error(
            CHECK,
            f"{n_leaked} test row(s) are identical to training rows ({frac:.1%} of test)",
            "Rows present in both splits let the model memorise answers it is later scored on, "
            "inflating test metrics.",
            evidence,
            fix="De-duplicate before splitting, or split on a unit/group id so duplicates stay together.",
        )
    return f.ok(CHECK, "No identical rows shared between train and test", evidence=evidence)
