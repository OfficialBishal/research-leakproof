"""How many of the 'samples' are actually independent."""

from __future__ import annotations

from .. import finding as f
from .._stats import as_1d, row_hashes

CHECK = "effective_n"


def run(ctx):
    if ctx.X is None and ctx.groups is None:
        return None

    threshold = ctx.option("effective_n_inflation", 2.0)
    evidence = {}
    inflations = []

    if ctx.X is not None:
        hashes = row_hashes(ctx.X)
        n = len(hashes)
        n_unique = len(set(hashes))
        evidence["n_rows"] = n
        evidence["n_unique_rows"] = n_unique
        if n_unique:
            inflations.append(("duplicate rows", n / n_unique))

    if ctx.groups is not None:
        g = as_1d(ctx.groups)
        n = g.size
        n_unique = len(set(g.tolist()))
        evidence["n_samples"] = int(n)
        evidence["n_unique_groups"] = n_unique
        if n_unique:
            inflations.append(("repeated groups", n / n_unique))

    if not inflations:
        return None

    worst_label, worst = max(inflations, key=lambda kv: kv[1])
    evidence["inflation_factor"] = round(worst, 2)
    evidence["driver"] = worst_label

    if worst >= threshold:
        return f.warn(
            CHECK,
            f"Effective sample size is ~{worst:.1f}x smaller than the reported count ({worst_label})",
            "Duplicated or grouped rows are not independent observations. Treating them as such "
            "overstates statistical power and shrinks honest confidence intervals.",
            evidence,
            fix="Report the number of independent units, and split / bootstrap / weight at the unit "
                "level rather than the row level.",
        )
    return f.ok(CHECK, "Sample count is close to the number of independent units", evidence=evidence)
