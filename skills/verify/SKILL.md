---
name: verify
description: Verify the numbers in a results write-up, report, or manuscript against the data and code that produced them. Use when the user is about to submit a paper, share results, or asks to double-check, fact-check, or reproduce the metrics in a document before publishing.
argument-hint: "[path to the report/manuscript]"
allowed-tools: Bash, Read, Grep, Glob, Write, Edit
---

# Verify a write-up's claims against the real numbers

Hold a document's quantitative claims to the data behind them, and flag any that are over-stated. Produce a short pass/fail passport the user can trust before they hit submit.

## 1. Extract the claims

Read the report/manuscript at `$ARGUMENTS`. Pull out every quantitative claim that can be re-checked: headline metrics (R2, correlation, MSE, accuracy, AUC), sample sizes, effect sizes, p-values, and any "X beats Y" comparison. Note for each the exact value and where it appears.

## 2. Recompute and compare

For each claim, find the artifact it came from (a predictions file, a metrics JSON, a results array) and recompute it directly. Compare against the stated value with a sensible tolerance; mark `PASS` if it matches, `FAIL` (with both numbers) if it does not, or `UNVERIFIABLE` if the source is missing.

Then run the rigor checks on the reported numbers with the bundled engine:

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python /tmp/leakproof_verify.py
```

```python
import leakproof
report = leakproof.audit(
    metrics={...},            # every metric the document reports
    n_test=...,               # test-set size, if stated
    effect_size=...,          # the headline effect as a correlation
    n_comparisons=...,        # how many results/ablations are reported
    corrected=...,            # whether a correction was applied
    predictions=..., targets=..., units=...,   # if available, to test for shape-collapse
)
print(report.to_text())
```

This catches the honesty problems a recomputation alone misses: a correlation quoted with no error metric, a claim below the detectable floor for the stated `n`, uncorrected multiple comparisons, or an aggregate score that collapses to per-unit means.

## 3. Write the passport

Emit a compact list the user can act on:

```
- [PASS] R2 = 0.30 on test (recomputed 0.301)
- [FAIL] "r = 0.48" -> recomputed 0.42; and r is reported without R2/MSE
- [WARN] effect r=0.10 is below the detectable floor (r=0.42) at n=82
- [UNVERIFIABLE] "p < 0.01" -> source computation not found
```

Offer to write it to a file and to fix the document's wording where a claim was over-stated.
