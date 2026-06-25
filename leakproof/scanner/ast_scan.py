"""Static scan of Python source for preprocessing fit on data before the split.

This is a deliberately conservative heuristic: it flags a transformer `.fit`/`.fit_transform`
that appears, by line number, before the first `train_test_split` in the same file. That ordering
is the classic way scaling/imputation/feature-selection statistics leak the test set into training.
"""

from __future__ import annotations

import ast
import os

from ..finding import Finding, Severity

CHECK = "preprocessing_leakage"

_FIT_METHODS = {"fit", "fit_transform"}
_SPLITTERS = {"train_test_split"}


def scan(path: str) -> list[Finding]:
    findings: list[Finding] = []
    for file in _python_files(path):
        try:
            with open(file, encoding="utf-8") as fh:
                tree = ast.parse(fh.read(), filename=file)
        except (SyntaxError, UnicodeDecodeError):
            continue
        findings.extend(_scan_tree(tree, file))
    return findings


def _python_files(path: str):
    if os.path.isfile(path):
        if path.endswith(".py"):
            yield path
        return
    for root, _, files in os.walk(path):
        if any(part in {".git", "__pycache__", ".venv", "node_modules"} for part in root.split(os.sep)):
            continue
        for name in files:
            if name.endswith(".py"):
                yield os.path.join(root, name)


def _scan_tree(tree: ast.AST, file: str) -> list[Finding]:
    fit_calls = []   # (lineno, label)
    split_lines = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _called_name(node.func)
        if name in _SPLITTERS:
            split_lines.append(node.lineno)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in _FIT_METHODS:
            if _looks_like_transform(node):
                fit_calls.append((node.lineno, node.func.attr))

    if not split_lines or not fit_calls:
        return []

    first_split = min(split_lines)
    out = []
    for lineno, method in fit_calls:
        if lineno < first_split:
            out.append(Finding(
                CHECK,
                Severity.WARN,
                f"Preprocessing `.{method}()` runs before train_test_split",
                "Fitting a scaler / imputer / feature selector on the full dataset leaks test-set "
                "statistics into training. Fit on the training split only.",
                evidence={"split_line": first_split},
                fix="Split first, then fit the transform on X_train and only transform X_test.",
                location=f"{file}:{lineno}",
            ))
    return out


def _called_name(func) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _looks_like_transform(node: ast.Call) -> bool:
    # fit_transform is transform-only; a bare fit with a single positional arg is too
    # (model.fit(X, y) takes two and is excluded to avoid false positives).
    if node.func.attr == "fit_transform":
        return True
    has_y_kw = any(kw.arg == "y" for kw in node.keywords)
    return len(node.args) <= 1 and not has_y_kw
