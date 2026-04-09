"""Unit tests for ``scripts/check_modified_test_decorators.py``.

The script isn't a package member, so we load it via importlib. Tests target
the pure ``find_violations`` core plus the hunk parser and the report
formatter; the git-shelling driver is not exercised here.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from textwrap import dedent

import pytest

_SCRIPT_PATH = Path(__file__).resolve().parents[3] / "scripts" / "check_modified_test_decorators.py"
_spec = importlib.util.spec_from_file_location("check_modified_test_decorators", _SCRIPT_PATH)
assert _spec is not None
assert _spec.loader is not None
check_mod = importlib.util.module_from_spec(_spec)
# Register BEFORE exec_module: @dataclass looks up sys.modules[cls.__module__]
# during class construction, which would otherwise return None and blow up with
# "'NoneType' object has no attribute '__dict__'".
sys.modules[_spec.name] = check_mod
_spec.loader.exec_module(check_mod)

find_violations = check_mod.find_violations
parse_hunk_line_numbers = check_mod.parse_hunk_line_numbers
format_report = check_mod.format_report
Violation = check_mod.Violation


def _all_lines(source: str) -> set[int]:
    return set(range(1, source.count("\n") + 2))


def test_added_test_without_decorator_is_violation() -> None:
    source = dedent(
        """
        def test_foo():
            x = 1
        """
    )
    violations = find_violations("f.py", source, _all_lines(source))
    assert len(violations) == 1
    assert violations[0].name == "test_foo"


def test_added_test_with_decorator_passes() -> None:
    source = dedent(
        """
        from tests.helpers.queries import assert_db_queries_num

        @assert_db_queries_num(5)
        def test_foo():
            x = 1
        """
    )
    assert find_violations("f.py", source, _all_lines(source)) == []


def test_added_test_with_bare_decorator_passes() -> None:
    # even without parens — still counts as "decorator present" for CI purposes
    source = dedent(
        """
        @assert_db_queries_num
        def test_foo():
            x = 1
        """
    )
    assert find_violations("f.py", source, _all_lines(source)) == []


def test_added_test_with_attribute_access_decorator_passes() -> None:
    source = dedent(
        """
        import tests.helpers.queries as q

        @q.assert_db_queries_num(5)
        def test_foo():
            x = 1
        """
    )
    assert find_violations("f.py", source, _all_lines(source)) == []


def test_added_test_with_no_query_assertion_marker_passes() -> None:
    source = dedent(
        """
        import pytest

        @pytest.mark.no_query_assertion
        def test_foo():
            x = 1
        """
    )
    assert find_violations("f.py", source, _all_lines(source)) == []


def test_added_test_with_fixture_in_body_passes() -> None:
    source = dedent(
        """
        def test_foo(django_assert_num_queries):
            with django_assert_num_queries(3):
                pass
        """
    )
    assert find_violations("f.py", source, _all_lines(source)) == []


def test_max_num_queries_fixture_also_passes() -> None:
    source = dedent(
        """
        def test_foo(django_assert_max_num_queries):
            with django_assert_max_num_queries(3):
                pass
        """
    )
    assert find_violations("f.py", source, _all_lines(source)) == []


def test_modified_body_line_in_legacy_test_is_violation() -> None:
    source = dedent(
        """
        def test_untouched():
            return 1

        def test_legacy():
            x = 1
            y = 2
        """
    ).lstrip("\n")
    # only line 6 (y = 2 inside test_legacy) is in the changed set
    source_lines = source.splitlines()
    y_line = next(i + 1 for i, ln in enumerate(source_lines) if "y = 2" in ln)
    violations = find_violations("f.py", source, {y_line})
    assert [v.name for v in violations] == ["test_legacy"]


def test_comment_only_edit_still_triggers_violation() -> None:
    source = dedent(
        """
        def test_legacy():
            # this comment just got changed
            x = 1
        """
    ).lstrip("\n")
    source_lines = source.splitlines()
    comment_line = next(i + 1 for i, ln in enumerate(source_lines) if "comment just got" in ln)
    violations = find_violations("f.py", source, {comment_line})
    assert [v.name for v in violations] == ["test_legacy"]


def test_non_test_helper_edit_is_not_violation() -> None:
    source = dedent(
        """
        def _helper():
            return 1

        def test_legacy():
            pass
        """
    ).lstrip("\n")
    source_lines = source.splitlines()
    helper_line = next(i + 1 for i, ln in enumerate(source_lines) if "return 1" in ln)
    assert find_violations("f.py", source, {helper_line}) == []


def test_class_based_test_method_without_decorator_is_violation() -> None:
    source = dedent(
        """
        class TestThing:
            def test_method(self):
                x = 1
        """
    ).lstrip("\n")
    violations = find_violations("f.py", source, _all_lines(source))
    assert [v.name for v in violations] == ["test_method"]


def test_untouched_test_is_not_violation() -> None:
    source = dedent(
        """
        def test_a():
            return 1

        def test_b():
            return 2
        """
    ).lstrip("\n")
    source_lines = source.splitlines()
    a_line = next(i + 1 for i, ln in enumerate(source_lines) if "return 1" in ln)
    violations = find_violations("f.py", source, {a_line})
    assert [v.name for v in violations] == ["test_a"]


def test_decorator_line_inside_changed_range_counts_as_touched() -> None:
    # Editing only the @decorator line of an otherwise-decorated test is fine;
    # editing the decorator of an undecorated test (no decorator present) can't
    # happen, but editing a decorator that isn't our decorator should flag.
    source = dedent(
        """
        import pytest

        @pytest.mark.django_db
        def test_foo():
            return 1
        """
    ).lstrip("\n")
    source_lines = source.splitlines()
    deco_line = next(i + 1 for i, ln in enumerate(source_lines) if "django_db" in ln)
    violations = find_violations("f.py", source, {deco_line})
    assert [v.name for v in violations] == ["test_foo"]


def test_syntax_error_file_yields_no_violations() -> None:
    assert find_violations("f.py", "def test_foo(:\n    pass\n", {1}) == []


# ---------- hunk header parser ----------


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("@@ -1,0 +2 @@", {2}),
        ("@@ -1,0 +2,3 @@", {2, 3, 4}),
        ("@@ -10,5 +20,0 @@", set()),  # pure deletion hunk
        ("@@ -1 +1 @@", {1}),
    ],
)
def test_parse_hunk_line_numbers_single(header: str, expected: set[int]) -> None:
    assert parse_hunk_line_numbers(header) == expected


def test_parse_hunk_line_numbers_multi_hunk() -> None:
    diff = (
        "diff --git a/f.py b/f.py\n"
        "--- a/f.py\n"
        "+++ b/f.py\n"
        "@@ -1,0 +2,2 @@\n"
        "+added line 2\n"
        "+added line 3\n"
        "@@ -10,1 +12,0 @@\n"
        "-removed"
    )
    assert parse_hunk_line_numbers(diff) == {2, 3}


# ---------- report formatter ----------


def test_format_report_groups_by_file_and_sorts() -> None:
    violations = [
        Violation(file="b.py", lineno=20, name="test_two"),
        Violation(file="a.py", lineno=10, name="test_one"),
        Violation(file="a.py", lineno=5, name="test_zero"),
    ]
    report = format_report(violations)
    a_idx = report.index("a.py")
    b_idx = report.index("b.py")
    assert a_idx < b_idx  # files sorted
    # within a.py, line 5 before line 10
    assert report.index("L5") < report.index("L10")
    assert "test_zero" in report
    assert "assert_db_queries_num" in report  # guidance footer present
    assert "no_query_assertion" in report
