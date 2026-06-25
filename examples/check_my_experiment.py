"""A template for gating an experiment on a research-leakproof audit.

Replace the placeholder loads with however your project stores its arrays, then run this at the
end of training/evaluation (or in CI). It exits non-zero if any error-level problem remains, so a
leaky or over-claimed result fails the build instead of reaching a paper.
"""

import sys

import research_leakproof as lp

# --- load what you have (every argument is optional) -------------------------
# X_train, X_test = ...                      # feature arrays per split
# g_train, g_test = ...                      # a group/subject id per sample, per split
# preds, y_true, units = ...                 # predictions, truth, and a unit id per sample
# metrics = {"pearson_r": ..., "r2": ..., "baseline_r2": ...}

report = lp.audit(
    # X_train=X_train, X_test=X_test,
    # groups_train=g_train, groups_test=g_test,
    # predictions=preds, targets=y_true, units=units,
    # metrics=metrics, n_test=len(y_true), effect_size=metrics["pearson_r"],
    # n_comparisons=1, corrected=False,
)

print(report)

if report.failed():
    sys.exit(1)
