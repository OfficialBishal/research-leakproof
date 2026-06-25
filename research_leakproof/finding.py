"""The result type every check returns."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Severity(str, Enum):
    ERROR = "error"   # a real correctness problem; fails CI by default
    WARN = "warn"     # likely a problem, depends on intent
    INFO = "info"     # worth knowing, not necessarily wrong
    OK = "ok"         # the check ran and found nothing

    @property
    def rank(self) -> int:
        return {"ok": 0, "info": 1, "warn": 2, "error": 3}[self.value]

    @property
    def symbol(self) -> str:
        return {"ok": "ok", "info": "i", "warn": "!", "error": "x"}[self.value]


@dataclass
class Finding:
    check: str                                   # check id, e.g. "split_leakage"
    severity: Severity
    title: str                                   # one-line summary
    detail: str = ""                             # what was found, in prose
    evidence: dict[str, Any] = field(default_factory=dict)  # the numbers behind it
    fix: str = ""                                # suggested remedy
    location: str = ""                           # file:line for static findings

    @property
    def passed(self) -> bool:
        return self.severity == Severity.OK

    def as_dict(self) -> dict[str, Any]:
        d = {
            "check": self.check,
            "severity": self.severity.value,
            "title": self.title,
            "detail": self.detail,
            "evidence": self.evidence,
            "fix": self.fix,
        }
        if self.location:
            d["location"] = self.location
        return d


def error(check, title, detail="", evidence=None, fix="", location=""):
    return Finding(check, Severity.ERROR, title, detail, evidence or {}, fix, location)


def warn(check, title, detail="", evidence=None, fix="", location=""):
    return Finding(check, Severity.WARN, title, detail, evidence or {}, fix, location)


def info(check, title, detail="", evidence=None, fix="", location=""):
    return Finding(check, Severity.INFO, title, detail, evidence or {}, fix, location)


def ok(check, title, detail="", evidence=None):
    return Finding(check, Severity.OK, title, detail, evidence or {})
