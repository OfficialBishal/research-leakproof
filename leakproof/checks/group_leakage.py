"""The same group/unit id appearing in both train and test."""

from __future__ import annotations

from .. import finding as f
from .._stats import as_1d

CHECK = "group_leakage"


def run(ctx):
    if ctx.groups_train is None or ctx.groups_test is None:
        return None

    train = set(as_1d(ctx.groups_train).tolist())
    test = set(as_1d(ctx.groups_test).tolist())
    leaked = sorted(train & test, key=str)

    evidence = {
        "n_train_groups": len(train),
        "n_test_groups": len(test),
        "n_leaked_groups": len(leaked),
        "example_leaked_groups": [str(g) for g in leaked[:10]],
    }
    if leaked:
        return f.error(
            CHECK,
            f"{len(leaked)} group(s) appear in both train and test",
            "When members of the same group straddle the split, the model can exploit "
            "group-specific signal it has already seen, so test scores do not measure generalisation.",
            evidence,
            fix="Use a grouped split (e.g. GroupKFold / GroupShuffleSplit) so every group is wholly "
                "in one side.",
        )
    return f.ok(CHECK, "No group spans both train and test", evidence=evidence)
