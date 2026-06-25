---
name: audit
description: Audit a machine-learning experiment or reported result for data leakage, inflated sample size, shape-collapse, and over-claimed metrics. Use when the user finishes a training or evaluation run, reports a model score (R2, correlation, accuracy, MSE), prepares results for a paper or report, or asks to check an experiment for leakage, rigor, soundness, or reproducibility.
argument-hint: "[path to results, predictions, or experiment dir]"
allowed-tools: Bash, Read, Grep, Glob, Write, Edit
---

# Audit an experiment for leakage and over-claimed results

Run the `research-leakproof` engine over whatever the user has, interpret the findings, and propose concrete fixes. The engine is deterministic Python; your job is to locate the right inputs and explain the results.

## 1. Find the inputs

Look at the experiment (use the path in `$ARGUMENTS` if given). Gather whatever exists — every input is optional and the matching check is simply skipped when absent:

| You found | Pass as | Catches |
| --- | --- | --- |
| train and test feature arrays | `X_train`, `X_test` | identical rows across the split |
| a group/subject/unit id per sample, per split | `groups_train`, `groups_test` | a group spanning both splits |
| a timestamp/order per sample, per split | `time_train`, `time_test` | training on the future |
| the full feature array or all group ids | `X`, `groups` | duplicated/grouped rows inflating N |
| model predictions, ground truth, and a unit id per sample | `predictions`, `targets`, `units` | high aggregate r with no within-unit signal |
| the reported metric names/values | `metrics={...}` | correlation reported without R2/MSE or a baseline |
| test-set size and the claimed effect | `n_test`, `effect_size` (a correlation) | a result below the detectable floor |
| number of comparisons and whether corrected | `n_comparisons`, `corrected` | uncorrected multiple testing |

Arrays may be `.npy`/`.npz`, CSV/parquet, or already in a script. Load them however they are stored.

## 2. Run the audit

Write a short script that imports `research_leakproof` and calls `audit(...)` with the inputs you gathered, then run it with the bundled engine on the path:

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python /tmp/research_leakproof_audit.py
```

The script body:

```python
import numpy as np
import research_leakproof as lp

report = lp.audit(
    # pass only what you actually have, e.g.:
    X_train=X_train, X_test=X_test,
    groups_train=g_train, groups_test=g_test,
    predictions=preds, targets=y_true, units=unit_ids,
    metrics={"pearson_r": 0.81, "r2": 0.30, "baseline_r2": 0.19},
    n_test=82, effect_size=0.30,
    n_comparisons=12, corrected=False,
)
print(report.to_text())
print(report.to_json())          # if you want the structured numbers
```

If the user prefers a permanent install instead of the bundled path: `pip install git+https://github.com/OfficialBishal/research-leakproof.git`, then drop the `PYTHONPATH=...` prefix.

## 3. Report back

- Lead with the count line (`N error / N warn / ...`) and whether it would fail CI (`report.failed()` is true when any error remains).
- For every non-OK finding, state the check, the number behind it (from `evidence`), and the one-line `fix`. Do not bury an `error` under passing checks.
- Be specific and non-accusatory: these are guardrails, not verdicts. If a finding is a known false positive, show how to suppress it (`suppress=["check_id"]` in the call, or a `research-leakproof.toml` with a `[suppress]` table).
- Offer to paste `report.integrity_block()` into the project's README, or to add the audit to CI / pre-commit so it runs on every change.
