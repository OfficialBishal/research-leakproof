"""Command-line entry point: `leakproof scan <path>`, `leakproof demo`, `leakproof version`."""

from __future__ import annotations

import argparse
import sys

from ._version import __version__
from .finding import Severity
from .report import Report
from .scanner import scan


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="leakproof",
        description="Catch data leakage and over-claimed results before a reviewer does.",
    )
    sub = parser.add_subparsers(dest="command")

    p_scan = sub.add_parser("scan", help="Statically scan Python source for leakage patterns.")
    p_scan.add_argument("paths", nargs="+", help="Files or directories to scan.")
    p_scan.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    p_scan.add_argument("--fail-on", choices=["error", "warn", "info"], default="warn",
                        help="Exit non-zero at this severity or worse (default: warn).")

    sub.add_parser("demo", help="Run the bundled leaky example and print the report.")
    sub.add_parser("version", help="Print the version.")

    args = parser.parse_args(argv)

    if args.command == "version":
        print(__version__)
        return 0

    if args.command == "demo":
        from .demo import make_report
        print(make_report().to_text())
        return 0

    if args.command == "scan":
        findings = []
        for path in args.paths:
            findings.extend(scan(path))
        report = Report(findings)
        print(report.to_json() if args.json else report.to_text())
        return 1 if report.failed(Severity(args.fail_on)) else 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
