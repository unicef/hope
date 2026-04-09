#!/usr/bin/env python3
"""Fail if any test function modified in this PR lacks a DB-query assertion.

Implements the "CI enforcement on modified tests" section of
``assert_num_queries_exact_decorator.md``. See that spec for the full rationale.

For each test file under ``--path-prefix`` that has hunks in the diff between
``HEAD`` and ``--base``, this script locates every ``def test_*`` (including
class-based test methods) whose source range intersects a changed line and
verifies it satisfies at least one of:

  1. decorated with ``@assert_db_queries_num(...)``
  2. decorated with ``@pytest.mark.no_query_assertion``
  3. calls ``django_assert_num_queries`` / ``django_assert_max_num_queries`` in body

Exits 0 on success, 1 with a grouped report on any violation. No third-party deps.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
import sys

# PoC scope: start narrow (just the two new currency pilot files), widen as
# the migration proceeds. Override with --path-prefix on the CLI.
DEFAULT_PATH_PREFIX = "tests/unit/apps/payment/test_currency_"

DECORATOR_NAME = "assert_db_queries_num"
MARKER_NAME = "no_query_assertion"
FIXTURE_NAMES = ("django_assert_num_queries", "django_assert_max_num_queries")

HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


@dataclass(frozen=True)
class Violation:
    file: str
    lineno: int
    name: str


def _decorator_target_name(node: ast.expr) -> str | None:
    """Return the terminal attribute/name referenced by a decorator expression."""
    target = node.func if isinstance(node, ast.Call) else node
    if isinstance(target, ast.Name):
        return target.id
    if isinstance(target, ast.Attribute):
        return target.attr
    return None


def _is_no_query_assertion_marker(node: ast.expr) -> bool:
    """Return True for ``@pytest.mark.no_query_assertion`` (bare or called)."""
    target = node.func if isinstance(node, ast.Call) else node
    if not isinstance(target, ast.Attribute) or target.attr != MARKER_NAME:
        return False
    parent = target.value
    if not (isinstance(parent, ast.Attribute) and parent.attr == "mark"):
        return False
    return isinstance(parent.value, ast.Name) and parent.value.id == "pytest"


def _has_query_assertion(func: ast.FunctionDef | ast.AsyncFunctionDef, source: str) -> bool:
    for deco in func.decorator_list:
        if _decorator_target_name(deco) == DECORATOR_NAME:
            return True
        if _is_no_query_assertion_marker(deco):
            return True
    body_src = ast.get_source_segment(source, func) or ""
    return any(name in body_src for name in FIXTURE_NAMES)


def _function_line_range(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
) -> tuple[int, int]:
    start = func.lineno
    for deco in func.decorator_list:
        start = min(start, deco.lineno)
    end = func.end_lineno or func.lineno
    return start, end


def _collect_test_functions(
    tree: ast.AST,
) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name.startswith("test_")
    ]


def find_violations(file_path: str, source: str, changed_lines: set[int]) -> list[Violation]:
    """Pure core: violations in a single file given its source and changed line numbers."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    violations: list[Violation] = []
    for func in _collect_test_functions(tree):
        start, end = _function_line_range(func)
        touched = any(start <= ln <= end for ln in changed_lines)
        if not touched:
            continue
        if _has_query_assertion(func, source):
            continue
        violations.append(Violation(file=file_path, lineno=func.lineno, name=func.name))
    return violations


def parse_hunk_line_numbers(diff_output: str) -> set[int]:
    """Extract new-side changed line numbers from ``git diff -U0`` output."""
    changed: set[int] = set()
    for line in diff_output.splitlines():
        m = HUNK_RE.match(line)
        if not m:
            continue
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) is not None else 1
        for i in range(count):
            changed.add(start + i)
    return changed


def _run_git(*args: str) -> str:
    cmd = ["git", *args]  # noqa: S607
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)  # noqa: S603
    return result.stdout


def _resolve_merge_base(base_ref: str) -> str:
    return _run_git("merge-base", base_ref, "HEAD").strip()


def _changed_files(merge_base: str, path_prefix: str) -> list[str]:
    out = _run_git("diff", "--name-only", merge_base, "HEAD", "--", path_prefix)
    return [line for line in out.splitlines() if line.endswith(".py")]


def _file_changed_lines(merge_base: str, file: str) -> set[int]:
    out = _run_git("diff", "-U0", merge_base, "HEAD", "--", file)
    return parse_hunk_line_numbers(out)


def format_report(violations: list[Violation]) -> str:
    by_file: dict[str, list[Violation]] = {}
    for v in violations:
        by_file.setdefault(v.file, []).append(v)
    lines: list[str] = []
    for file in sorted(by_file):
        lines.append(file)
        lines.extend(f"  L{v.lineno}  {v.name}" for v in sorted(by_file[file], key=lambda v: v.lineno))
        lines.append("")
    lines.append(
        "These tests were modified in this PR but do not assert their DB query count.\n"
        "Add @assert_db_queries_num(N) (see assert_num_queries_exact_decorator.md),\n"
        "or, if the test genuinely does not touch the ORM, mark it with\n"
        "@pytest.mark.no_query_assertion."
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        default="origin/develop",
        help="Base ref to diff against (default: origin/develop)",
    )
    parser.add_argument(
        "--path-prefix",
        default=DEFAULT_PATH_PREFIX,
        help=f"Only check test files under this prefix (default: {DEFAULT_PATH_PREFIX})",
    )
    args = parser.parse_args(argv)

    merge_base = _resolve_merge_base(args.base)
    changed_files = _changed_files(merge_base, args.path_prefix)

    violations: list[Violation] = []
    for file in changed_files:
        path = Path(file)
        if not path.exists():
            continue
        source = path.read_text()
        changed_lines = _file_changed_lines(merge_base, file)
        violations.extend(find_violations(file, source, changed_lines))

    if not violations:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
