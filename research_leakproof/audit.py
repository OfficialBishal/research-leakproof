"""The audit() entrypoint and the context object the checks read from."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .checks import RUNTIME_CHECKS
from .report import Report
from .suppress import apply_suppressions


@dataclass
class AuditContext:
    # Row-level splits
    X_train: Any = None
    X_test: Any = None
    # Group ids per split (for grouped-split leakage)
    groups_train: Any = None
    groups_test: Any = None
    # Timestamps per split (for look-ahead leakage)
    time_train: Any = None
    time_test: Any = None
    # Whole dataset (for effective sample size)
    X: Any = None
    groups: Any = None
    # Model outputs (for shape collapse)
    predictions: Any = None
    targets: Any = None
    units: Any = None
    # Reported numbers (for honesty / power / multiplicity)
    metrics: Any = None
    n_test: int | None = None
    effect_size: float | None = None
    effect_r2: float | None = None
    n_comparisons: int | None = None
    corrected: bool = False
    # Findings to drop or downgrade, plus tunable thresholds
    suppress: Any = None
    options: dict = field(default_factory=dict)

    def option(self, key, default):
        return self.options.get(key, default)


def audit(**kwargs) -> Report:
    """Run every applicable check over the inputs you supply and return a Report.

    Pass only what you have: each check that lacks its inputs is skipped. See the README
    for the full list of accepted keywords.
    """
    options = kwargs.pop("options", None) or {}
    # Convenience: let thresholds like alpha/power pass straight through to options.
    for k in ("alpha", "power"):
        if k in kwargs:
            options.setdefault(k, kwargs.pop(k))
    suppress = kwargs.pop("suppress", None)

    valid = {f.name for f in AuditContext.__dataclass_fields__.values()}
    unknown = set(kwargs) - valid
    if unknown:
        raise TypeError(f"audit() got unexpected keyword(s): {', '.join(sorted(unknown))}")

    ctx = AuditContext(suppress=suppress, options=options, **kwargs)

    findings = []
    for check in RUNTIME_CHECKS:
        result = check.run(ctx)
        if result is not None:
            findings.append(result)

    findings = apply_suppressions(findings, ctx.suppress)
    return Report(findings)
