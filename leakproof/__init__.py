"""leakproof - catch data leakage and over-claimed results in research code.

Typical use:

    import leakproof
    report = leakproof.audit(X_train=Xtr, X_test=Xte, groups_train=gtr, groups_test=gte)
    print(report)
    if report.failed():
        raise SystemExit(1)
"""

from ._version import __version__
from .audit import AuditContext, audit
from .finding import Finding, Severity
from .report import Report
from .scanner import scan

__all__ = ["audit", "scan", "Report", "Finding", "Severity", "AuditContext", "__version__"]
