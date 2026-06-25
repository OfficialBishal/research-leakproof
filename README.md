# research-leakproof

Catch the silent ways a result lies — data leakage, inflated sample size, shape-collapse, and
over-claimed metrics — before a reviewer does. It runs as a [Claude Code](https://claude.com/claude-code)
plugin and as a small Python library, on any field's data.

![license](https://img.shields.io/badge/license-MIT-blue) ![python](https://img.shields.io/badge/python-3.9%2B-blue)

Experiment trackers (Weights & Biases, MLflow, DVC) record *what* you ran. They do not tell you the
test set leaked into training, that your 14,000 "samples" are 500 rows copied 28 times, or that a
headline correlation collapses to nothing once you look within each subject. `research-leakproof`
checks for exactly those failures and explains each one with the number behind it and how to fix it.

## What it catches

| Check | What it flags |
| --- | --- |
| `split_leakage` | Rows that are identical across the train and test split |
| `group_leakage` | A subject / group / unit id that appears in both splits |
| `temporal_leakage` | Training timestamps that reach into or past the test period |
| `effective_n` | Duplicated or grouped rows inflating the apparent sample size |
| `shape_collapse` | A high aggregate correlation that hides near-zero per-unit signal |
| `metric_honesty` | A correlation reported with no error metric (R²/MSE) or baseline |
| `power` | A claimed effect below the smallest the test set can detect |
| `multiple_comparisons` | Many results reported with no multiple-testing correction |
| `preprocessing_leakage` | (static scan) Scaler/imputer/selector fit on the full data before the split |

Every input is optional: each check runs only when you supply the data it needs, and is skipped
otherwise. Nothing here is domain-specific — it works on tabular data, images, text, genomics, or
anything else with a train/test split and a metric.

## Use it in Claude Code

```
/plugin marketplace add OfficialBishal/research-leakproof
/plugin install research-leakproof@research-leakproof
```

Then just finish a run and ask Claude to check it, or call a skill directly:

- `/research-leakproof:audit` — audit an experiment's splits, predictions, and reported metrics
- `/research-leakproof:verify` — verify the numbers in a report or manuscript against the data
- `/research-leakproof:scan` — statically scan your code for leakage patterns

The skills also trigger on their own when you report a metric or prepare results, so the audit
happens without you remembering to ask.

## Use it as a library or in CI

```bash
pip install git+https://github.com/OfficialBishal/research-leakproof.git
```

```python
import leakproof

report = leakproof.audit(
    X_train=X_train, X_test=X_test,
    groups_train=g_train, groups_test=g_test,
    predictions=preds, targets=y_true, units=unit_ids,
    metrics={"pearson_r": 0.81, "r2": 0.30, "baseline_r2": 0.19},
    n_test=82, effect_size=0.30,
    n_comparisons=12, corrected=False,
)

print(report)                 # human-readable
report.to_json()              # structured, for logging
report.integrity_block()      # paste-in pass/fail block for a README or paper

if report.failed():           # true if any error remains
    raise SystemExit(1)
```

Scan source without running it:

```bash
leakproof scan path/to/project        # or: python -m leakproof scan .
leakproof demo                        # run a built-in leaky example
```

## Example

`leakproof demo` runs a small experiment with planted problems:

```
[x] split_leakage: 2 test row(s) are identical to training rows (4.8% of test)
[x] group_leakage: 1 group(s) appear in both train and test
[x] shape_collapse: Aggregate r=0.95, but predictions barely vary within a unit
[!] temporal_leakage: 10 training point(s) fall at or after the test period begins
[!] effective_n: Effective sample size is ~8.0x smaller than the reported count (repeated groups)
[!] metric_honesty: A correlation metric is reported without an error metric
[!] power: Underpowered: claimed effect r=0.10 is below the detectable floor r=0.42 at n=42
[!] multiple_comparisons: 12 comparisons reported with no multiple-testing correction
----------------------------------------
3 error  5 warn  0 info  0 ok
```

Each finding prints the number behind it and a one-line fix (trimmed above for brevity).

## How a few of them work

- **shape_collapse** removes each unit's mean from both predictions and targets, then measures how
  much the prediction still moves *within* a unit relative to the target. A model that predicts one
  value per unit scores a strong aggregate correlation while explaining none of the within-unit
  variation — this is the check that catches it.
- **effective_n** content-hashes rows (and counts unique groups) to estimate how many independent
  observations you really have, so confidence intervals are not computed against copies.
- **power** uses the Fisher-z normal approximation to report the smallest correlation your test set
  can distinguish from noise, and warns when a claimed effect falls below it.

## Suppressing false positives

A check is conservative, but if one fires on something you have justified, name it:

```python
leakproof.audit(..., suppress=["temporal_leakage"])
```

or add a `leakproof.toml` to the project:

```toml
[suppress]
temporal_leakage = "splits are random by design, not time-ordered"
```

A suppressed finding is downgraded to a note rather than dropped, so it stays visible.

## Enforce it automatically

Pre-commit (`.pre-commit-config.yaml`):

```yaml
- repo: https://github.com/OfficialBishal/research-leakproof
  rev: v0.1.0
  hooks:
    - id: leakproof-scan
```

Or copy `.github/workflows/ci.yml` to run `pytest` and `leakproof scan` on every push.

## Why not just an experiment tracker?

| | tracks runs | detects leakage | flags over-claimed metrics | runs in Claude Code |
| --- | :---: | :---: | :---: | :---: |
| W&B / MLflow | yes | no | no | no |
| DVC | yes | no | no | no |
| leakr (R only) | no | yes | no | no |
| **research-leakproof** | no | **yes** | **yes** | **yes** |

They are complementary: track with one, validate with this.

## License

MIT
