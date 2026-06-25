# Changelog

## 0.1.0

First release.

- `leakproof.audit(...)` runtime checks: split leakage, group leakage, temporal leakage,
  effective sample size, shape-collapse, metric honesty, statistical power, and multiple comparisons.
- `leakproof scan` static check for preprocessing fit before the train/test split.
- Text, Markdown, and JSON reports, plus a paste-in integrity block.
- Suppression via argument, or a `leakproof.toml` `[suppress]` table.
- Claude Code plugin with `audit`, `verify`, and `scan` skills.
- Pre-commit hook and GitHub Actions workflow.
