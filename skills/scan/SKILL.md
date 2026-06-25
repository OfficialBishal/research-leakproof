---
name: scan
description: Statically scan Python source for data-leakage patterns such as fitting a scaler, imputer, or feature selector on the full dataset before the train/test split. Use when the user wants to check a codebase or script for leakage without running it, or to wire leakage checks into pre-commit or CI.
argument-hint: "[file or directory to scan]"
allowed-tools: Bash, Read, Grep, Glob
---

# Scan code for leakage patterns

Run the static scanner over the target (default to the project if `$ARGUMENTS` is empty):

```bash
PYTHONPATH="${CLAUDE_PLUGIN_ROOT}" python -m leakproof scan "$ARGUMENTS"
```

Add `--json` for structured output, or `--fail-on error` to only fail CI on errors. The scanner reads source with Python's `ast` and never executes it, so it is safe to run anywhere.

For each finding, show the `file:line`, explain why the pattern leaks (fitting preprocessing on all the data lets test-set statistics into training), and propose the fix: split first, fit the transform on `X_train`, then transform `X_test`.

If the user wants this enforced automatically, offer to add the bundled pre-commit hook (`.pre-commit-hooks.yaml`) or the GitHub Actions workflow (`.github/workflows/ci.yml`) to their project.
