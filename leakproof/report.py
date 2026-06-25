"""Collects findings and renders them as text, Markdown, or JSON."""

from __future__ import annotations

import json

from .finding import Finding, Severity

_ORDER = [Severity.ERROR, Severity.WARN, Severity.INFO, Severity.OK]


class Report:
    def __init__(self, findings: list[Finding]):
        self.findings = findings

    # --- summary ---------------------------------------------------------
    def counts(self) -> dict[str, int]:
        c = {s.value: 0 for s in _ORDER}
        for f in self.findings:
            c[f.severity.value] += 1
        return c

    @property
    def worst(self) -> Severity:
        return max((f.severity for f in self.findings), key=lambda s: s.rank, default=Severity.OK)

    def failed(self, fail_on: Severity = Severity.ERROR) -> bool:
        return any(f.severity.rank >= fail_on.rank and f.severity != Severity.OK
                   for f in self.findings)

    def problems(self) -> list[Finding]:
        return [f for f in self.findings if f.severity != Severity.OK]

    # --- renderers -------------------------------------------------------
    def to_dict(self) -> dict:
        return {"counts": self.counts(), "findings": [f.as_dict() for f in self.findings]}

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_text(self) -> str:
        lines = ["leakproof report", "=" * 40]
        for sev in _ORDER:
            for f in [x for x in self.findings if x.severity == sev]:
                head = f"[{f.severity.symbol}] {f.check}: {f.title}"
                lines.append(head)
                if f.severity == Severity.OK:
                    continue
                if f.location:
                    lines.append(f"      at {f.location}")
                if f.detail:
                    lines.append(f"      {f.detail}")
                if f.fix:
                    lines.append(f"      fix: {f.fix}")
        c = self.counts()
        lines.append("-" * 40)
        lines.append(f"{c['error']} error  {c['warn']} warn  {c['info']} info  {c['ok']} ok")
        return "\n".join(lines)

    def to_markdown(self) -> str:
        c = self.counts()
        lines = [
            "## leakproof report",
            "",
            f"**{c['error']} error · {c['warn']} warn · {c['info']} info · {c['ok']} ok**",
            "",
            "| severity | check | finding |",
            "| --- | --- | --- |",
        ]
        for sev in _ORDER:
            for f in [x for x in self.findings if x.severity == sev]:
                lines.append(f"| {f.severity.value} | `{f.check}` | {f.title} |")
        return "\n".join(lines)

    def integrity_block(self) -> str:
        """A compact pass/fail block to paste into a README or paper appendix."""
        lines = ["<!-- leakproof integrity block -->", "Research integrity checks:"]
        for f in self.findings:
            mark = "PASS" if f.severity == Severity.OK else f.severity.value.upper()
            lines.append(f"- [{mark}] {f.check}: {f.title}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_text()

    def __repr__(self) -> str:
        c = self.counts()
        return f"<Report {c['error']}E/{c['warn']}W/{c['info']}I/{c['ok']}OK>"
