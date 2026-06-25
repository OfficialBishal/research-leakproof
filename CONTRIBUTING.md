# Contributing

Thanks for taking a look. The project is small on purpose, so contributions are easy to reason about.

## Development

```bash
git clone https://github.com/OfficialBishal/research-leakproof.git
cd research-leakproof
pip install -e ".[dev]"
pytest
```

## Adding a check

Each check is a single module under `leakproof/checks/` with one function:

```python
def run(ctx):
    if ctx.some_input is None:
        return None          # not enough information; the check is skipped
    ...
    return finding.warn(CHECK, "short title", "what was found", evidence={...}, fix="how to fix")
```

Then register it in `leakproof/checks/__init__.py`. Every check needs two tests in `tests/`: one
where it fires on a leaky fixture and one where it stays silent on a clean fixture. Checks should be
conservative — a false positive that cannot be suppressed is worse than a missed edge case.

## Principles

- NumPy is the only required dependency. Keep it that way unless there is a strong reason.
- Findings carry the numbers behind them in `evidence`, and a one-line `fix`.
- Prefer measuring the data over guessing from source. Static scanning is a fallback, not the default.
