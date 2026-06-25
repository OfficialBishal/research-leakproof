"""Render the bundled demo report as a terminal-style SVG for the README.

Run from the repo root:  python assets/render_demo_svg.py
The output (assets/demo.svg) is generated from the real `research-leakproof demo` output, so it stays honest.
"""

from __future__ import annotations

import os
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_leakproof.demo import make_report  # noqa: E402
from research_leakproof.finding import Severity  # noqa: E402

COLOR = {
    Severity.ERROR: "#ff6b6b",
    Severity.WARN: "#e6b450",
    Severity.INFO: "#6cb6ff",
    Severity.OK: "#7ee787",
}
FG = "#c9d1d9"
DIM = "#8b949e"
BG = "#0d1117"
BAR = "#161b22"

CHAR_W = 7.75
FONT = 13
LINE_H = 21
PAD = 18
HEADER = 34


def lines_from(report):
    order = [Severity.ERROR, Severity.WARN, Severity.INFO, Severity.OK]
    rows = []
    for sev in order:
        for f in (x for x in report.findings if x.severity == sev and x.severity != Severity.OK):
            rows.append((f"[{f.severity.symbol}] {f.check}: {f.title}", COLOR[sev]))
    c = report.counts()
    rows.append(("", FG))
    rows.append((f"{c['error']} error   {c['warn']} warn   {c['info']} info   {c['ok']} ok", DIM))
    return rows


def render(rows) -> str:
    max_chars = max([len(t) for t, _ in rows] + [len("$ research-leakproof demo")])
    width = int(PAD * 2 + max_chars * CHAR_W) + 24
    n_text_rows = 1 + len(rows)  # the command line plus the output rows
    height = int(HEADER + PAD * 2 + n_text_rows * LINE_H)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        # Animation reveals each line; base opacity is 1, so it stays readable where
        # SVG animation is disabled (the static fallback).
        "<style>text{animation:fin .45s backwards}@keyframes fin{from{opacity:0}to{opacity:1}}</style>",
        f'<rect width="{width}" height="{height}" rx="10" fill="{BG}"/>',
        f'<rect width="{width}" height="{HEADER}" rx="10" fill="{BAR}"/>',
        f'<rect y="{HEADER - 10}" width="{width}" height="10" fill="{BAR}"/>',
        '<circle cx="20" cy="17" r="6" fill="#ff5f56"/>',
        '<circle cx="40" cy="17" r="6" fill="#ffbd2e"/>',
        '<circle cx="60" cy="17" r="6" fill="#27c93f"/>',
        f'<text x="{width / 2}" y="22" fill="{DIM}" font-size="12" text-anchor="middle" '
        'style="animation:none">research-leakproof</text>',
    ]

    y = HEADER + PAD + FONT
    out.append(
        f'<text x="{PAD}" y="{y}" font-size="{FONT}" style="animation-delay:.1s">'
        f'<tspan fill="{COLOR[Severity.OK]}">$</tspan>'
        f'<tspan fill="{FG}"> research-leakproof demo</tspan></text>'
    )
    y += LINE_H
    delay = 0.55
    for text, color in rows:
        if text:
            out.append(
                f'<text x="{PAD}" y="{y}" fill="{color}" font-size="{FONT}" '
                f'xml:space="preserve" style="animation-delay:{delay:.2f}s">{escape(text)}</text>'
            )
            delay += 0.18
        y += LINE_H
    out.append("</svg>")
    return "\n".join(out)


def main():
    svg = render(lines_from(make_report()))
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
