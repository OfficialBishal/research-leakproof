"""Many tests reported without correcting the significance threshold."""

from __future__ import annotations

from .. import finding as f

CHECK = "multiple_comparisons"


def run(ctx):
    if ctx.n_comparisons is None:
        return None

    n = int(ctx.n_comparisons)
    if n <= 1:
        return f.ok(CHECK, "Single comparison; no correction needed", evidence={"n_comparisons": n})

    alpha = ctx.option("alpha", 0.05)
    corrected = bool(ctx.corrected)
    evidence = {
        "n_comparisons": n,
        "alpha": alpha,
        "bonferroni_alpha": round(alpha / n, 6),
        "corrected": corrected,
    }
    if not corrected:
        return f.warn(
            CHECK,
            f"{n} comparisons reported with no multiple-testing correction",
            "Running many tests at the same threshold inflates the chance of a false positive. "
            f"At alpha={alpha} over {n} tests, expect roughly {alpha * n:.1f} spurious hit(s).",
            evidence,
            fix=f"Apply Bonferroni (alpha/{n} = {alpha / n:.4f}) or Benjamini-Hochberg FDR control, and "
                "set corrected=True once you have.",
        )
    return f.ok(CHECK, "Multiple comparisons acknowledged as corrected", evidence=evidence)
