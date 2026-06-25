"""Suppressing known false positives.

A suppression is just a check id. Supply them as a list/set, a dict {id: reason}, or a
path to a TOML file with a `[suppress]` table whose keys are check ids.
"""

from __future__ import annotations

import os

from .finding import Finding, Severity

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None


def normalise(suppress) -> set[str]:
    if suppress is None:
        return set()
    if isinstance(suppress, str) and os.path.exists(suppress):
        return load_toml(suppress)
    if isinstance(suppress, dict):
        return {str(k) for k in suppress}
    if isinstance(suppress, str):
        return {suppress}
    return {str(s) for s in suppress}


def load_toml(path: str) -> set[str]:
    if tomllib is None:  # pragma: no cover
        raise RuntimeError("Reading a TOML suppress file needs Python 3.11+ (tomllib).")
    with open(path, "rb") as fh:
        data = tomllib.load(fh)
    table = data.get("suppress", data)
    return {str(k) for k in table}


def apply_suppressions(findings: list[Finding], suppress) -> list[Finding]:
    ids = normalise(suppress)
    if not ids:
        return findings
    out = []
    for f in findings:
        if f.check in ids and f.severity != Severity.OK:
            out.append(Finding(f.check, Severity.INFO, f"[suppressed] {f.title}", f.detail,
                               f.evidence, f.fix, f.location))
        else:
            out.append(f)
    return out
