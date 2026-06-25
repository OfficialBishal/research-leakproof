"""Whether the test set is large enough to detect the claimed effect."""

from __future__ import annotations

import math

from .. import finding as f
from .._stats import mde_correlation

CHECK = "power"


def run(ctx):
    if ctx.n_test is None:
        return None

    alpha = ctx.option("alpha", 0.05)
    power = ctx.option("power", 0.80)
    mde_r = mde_correlation(ctx.n_test, power=power, alpha=alpha)
    if not math.isfinite(mde_r):
        return None

    # Accept the claimed effect as a correlation, or convert from an R^2.
    effect_r = None
    if ctx.effect_size is not None:
        effect_r = abs(float(ctx.effect_size))
    elif ctx.effect_r2 is not None:
        effect_r = math.sqrt(abs(float(ctx.effect_r2)))

    evidence = {
        "n_test": ctx.n_test,
        "power": power,
        "alpha": alpha,
        "min_detectable_r": round(mde_r, 4),
        "min_detectable_r2": round(mde_r ** 2, 4),
    }
    if effect_r is not None:
        evidence["claimed_effect_r"] = round(effect_r, 4)
        if effect_r < mde_r:
            return f.warn(
                CHECK,
                f"Underpowered: claimed effect r={effect_r:.2f} is below the detectable floor "
                f"r={mde_r:.2f} at n={ctx.n_test}",
                "With this test size, an effect this small is indistinguishable from noise, so a "
                "non-significant (or significant) result is not trustworthy on its own.",
                evidence,
                fix="Increase the test size, pool datasets, or report the effect with its confidence "
                    "interval and the minimum detectable effect.",
            )
        return f.ok(
            CHECK,
            f"Test size n={ctx.n_test} can detect the claimed effect (r={effect_r:.2f} >= "
            f"{mde_r:.2f})",
            evidence=evidence,
        )

    return f.info(
        CHECK,
        f"At n={ctx.n_test} the smallest detectable effect is about r={mde_r:.2f} "
        f"(R^2={mde_r ** 2:.2f})",
        "Anything weaker than this is below the noise floor for this test size.",
        evidence,
    )
