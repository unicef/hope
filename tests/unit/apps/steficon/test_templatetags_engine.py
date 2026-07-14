from types import SimpleNamespace

import pytest

from extras.test_utils.factories.steficon import RuleCommitFactory, RuleFactory
from hope.apps.steficon.templatetags.engine import HtmlDiff, define, diff, get_attr, get_item, pygmentize


@pytest.fixture
def rule():
    return RuleFactory(definition="result.value = 100")


@pytest.fixture
def first_commit(rule):
    return RuleCommitFactory(rule=rule, before={}, after={"definition": "result.value = 1"})


@pytest.fixture
def second_commit(rule, first_commit):
    return RuleCommitFactory(
        rule=rule,
        before={"definition": "result.value = 1"},
        after={"definition": "result.value = 2"},
    )


def test_html_diff_make_table_produces_html():
    html_diff = HtmlDiff()
    result = html_diff.make_table(["line1\n", "line2\n"], ["line1\n", "changed\n"], "before", "after")
    assert "<table" in result
    assert "before" in result
    assert "after" in result


def test_html_diff_make_table_without_descriptions_has_no_header():
    html_diff = HtmlDiff()

    result = html_diff.make_table(["line1\n"], ["changed\n"])

    assert "<thead>" not in result


def test_html_diff_make_table_context_splits_change_groups_into_tbodies():
    html_diff = HtmlDiff()
    fromlines = ["first_a\n"] + ["same\n"] * 30 + ["last_a\n"]
    tolines = ["first_b\n"] + ["same\n"] * 30 + ["last_b\n"]

    result = html_diff.make_table(fromlines, tolines, "before", "after", context=True, numlines=1)

    assert result.count("<tbody>") == 2


def test_html_diff_format_line_without_side_skips_id_and_escapes():
    html_diff = HtmlDiff()
    html_diff._make_prefix()

    result = html_diff._format_line(None, "", 1, "a < b")

    assert 'id="' not in result
    assert "&lt;" in result


def test_get_attr_returns_attribute_value():
    assert get_attr(SimpleNamespace(foo="bar"), "foo") == "bar"


def test_define_returns_value():
    assert define("x") == "x"


def test_get_item_returns_dict_value():
    assert get_item({"key": "value"}, "key") == "value"


def test_pygmentize_highlights_code():
    result = pygmentize("result.value = 1")

    assert "highlight" in result


@pytest.mark.django_db
def test_diff_before_after_on_first_commit_shows_no_data_label(first_commit):
    result = diff(first_commit, "before,after")

    assert "No Data (First Commit" in result
    assert f"Version after commit ({first_commit.version})" in result


@pytest.mark.django_db
def test_diff_before_after_on_second_commit_shows_previous_version_label(first_commit, second_commit):
    result = diff(second_commit, "before,after")

    assert f"Version before commit ({first_commit.version})" in result
    assert f"Version after commit ({second_commit.version})" in result


@pytest.mark.django_db
def test_diff_after_current_shows_commit_and_current_labels(rule, second_commit):
    result = diff(second_commit, "after,current")

    assert f"Version commit ({second_commit.version})" in result
    assert f"Version current ({rule.version})" in result


@pytest.mark.django_db
def test_diff_before_current_shows_double_space_commit_label(rule, second_commit):
    result = diff(second_commit, "before,current")

    assert f"Version  commit ({second_commit.version})" in result
    assert f"Version current ({rule.version})" in result


def test_diff_invalid_panels_raises_exception():
    commit = SimpleNamespace(rule=None)

    with pytest.raises(Exception, match="Invalid value for panels"):
        diff(commit, "wrong,panels")
